import functools
import json
import idaapi
import ida_hexrays
import ida_kernwin
import idc
import idautils
import ida_ua
import ida_funcs
import ida_name
import ida_bytes
import ida_segment
import ida_nalt
import ida_ida
import os
import re
import textwrap
import threading
import requests
import ida_typeinf
import ida_idaapi
import ida_xref
# Set your API key here, or put in in the OPENROUTER_API_KEY environment variable.
OPENROUTER_API_KEY = "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"
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
OPENROUTER_MODEL = "google/gemini-2.5-flash-preview-05-20:thinking"  # Default model, can be changed

# Framework context with more balanced description
FRAMEWORK_CONTEXT = {
    "name": "Promon Shield",
    "type": "Mobile Protection Framework",
    "platform": "iOS",
    "application": "Brawl Stars",
    "description": "Promon Shield (PRMShield) is a protection framework used in the iOS game Brawl Stars that implements various security mechanisms during app initialization.",
    "common_features": [
        "Jailbreak detection",
        "Anti-debugging mechanisms",
        "Runtime attestation",
        "Hook detection (e.g., Frida or Stalker detection)",
        "Environmental integrity checks"
    ],
    "common_patterns": [
        "Security checks and validations",
        "File integrity verification",
        "Environment scanning",
        "Anti-tampering measures",
        "Configuration file processing ('li.txt', 'bi.txt', 'config-encrypt.txt')"
    ]
}


def decompile_function(function_addr):

    try:
        func = ida_hexrays.decompile(function_addr)
        if func:
            return str(func)
        return None
    except:
        return None


# Add this improved function to detect more called functions, including indirect calls
def get_enhanced_called_functions(func_ea):

    func = idaapi.get_func(func_ea)
    if not func:
        return [], {}
    
    called_funcs = []
    call_count = {}
    
    # Method 1: Use existing direct call detection
    for instr_addr in idautils.FuncItems(func.start_ea):
        if idaapi.is_call_insn(instr_addr):
            insn = ida_ua.insn_t()
            if ida_ua.decode_insn(insn, instr_addr) > 0:
                for i in range(0, 5):  # Check operands
                    if insn.ops[i].type == ida_ua.o_near or insn.ops[i].type == ida_ua.o_mem:
                        target_addr = insn.ops[i].addr
                        target_func = ida_funcs.get_func(target_addr)
                        if target_func:
                            target_name = ida_funcs.get_func_name(target_addr)
                            if target_name in call_count:
                                call_count[target_name] += 1
                            else:
                                call_count[target_name] = 1
                                called_funcs.append((target_name, target_addr))
                            break
    
    try:
        # Try to use Flowchart to find potential calls
        flowchart = idaapi.FlowChart(func)
        for block in flowchart:
            for succ_block in block.succs():
                # Check if successor block is outside this function
                if succ_block.start_ea < func.start_ea or succ_block.start_ea >= func.end_ea:
                    # This might be a call to another function
                    target_func = ida_funcs.get_func(succ_block.start_ea)
                    if target_func and target_func.start_ea != func.start_ea:
                        target_name = ida_funcs.get_func_name(target_func.start_ea)
                        if target_name in call_count:
                            call_count[target_name] += 1
                        else:
                            call_count[target_name] = 1
                            called_funcs.append((target_name, target_func.start_ea))
    except:
        print("[DEBUG] FlowChart analysis failed")
    
    for instr_addr in idautils.FuncItems(func.start_ea):
        for xref in idautils.CodeRefsFrom(instr_addr, 0):
            if xref != ida_idaapi.BADADDR:
                target_func = ida_funcs.get_func(xref)
                if target_func and target_func.start_ea != func.start_ea:
                    target_name = ida_funcs.get_func_name(target_func.start_ea)
                    if target_name in call_count:
                        call_count[target_name] += 1
                    else:
                        call_count[target_name] = 1
                        called_funcs.append((target_name, target_func.start_ea))
    
    # Remove duplicates while preserving count information
    unique_called_funcs = []
    seen = set()
    for name, addr in called_funcs:
        if name not in seen:
            seen.add(name)
            unique_called_funcs.append((name, addr))
    
    print(f"[DEBUG] Enhanced detection found {len(unique_called_funcs)} unique called functions")
    return unique_called_funcs, call_count
def get_function_xrefs_from(func_ea):

    xrefs_from = []
    seen = set()
    
    # Iterate through all instructions in the function
    for instr_addr in idautils.FuncItems(func_ea):
        for xref in idautils.XrefsFrom(instr_addr, 0):
            # Skip if we've already seen this destination
            if xref.to in seen:
                continue
                
            # Skip if the xref is within the same function
            target_func = ida_funcs.get_func(xref.to)
            if target_func and target_func.start_ea == func_ea:
                continue
                
            seen.add(xref.to)
            
            # Get symbol name if available
            name = ida_name.get_name(xref.to)
            if not name:
                name = f"unnamed_{hex(xref.to)}"
                
            # Determine the type of reference
            ref_type = "Code" if xref.type in [ida_xref.fl_CN, ida_xref.fl_CF] else "Data"
            
            # Try to get any string at this address
            str_content = None
            if ref_type == "Data":
                possible_str = ida_bytes.get_strlit_contents(xref.to, -1, ida_nalt.STRTYPE_C)
                if possible_str:
                    try:
                        str_content = possible_str.decode('utf-8', errors='replace')
                    except:
                        str_content = str(possible_str)
            
            xrefs_from.append({
                "name": name,
                "address": xref.to,
                "type": ref_type,
                "string_content": str_content
            })
    
    return xrefs_from
def get_enhanced_called_functions(func_ea, lite=False):
    func = idaapi.get_func(func_ea)
    if not func:
        return [], {}

    called_funcs = []
    call_count = {}

    # Method 1: Use existing direct call detection
    for instr_addr in idautils.FuncItems(func.start_ea):
        if idaapi.is_call_insn(instr_addr):
            insn = ida_ua.insn_t()
            if ida_ua.decode_insn(insn, instr_addr) > 0:
                # Iterate through the operands. Most architectures have at most 6-8 operands.
                # insn.ops is a list-like structure.
                # We check op.type != ida_ua.o_void to see if the operand is used.
                for i in range(len(insn.ops)): # More Pythonic: iterate the actual ops list
                    op = insn.ops[i]
                    if op.type == ida_ua.o_void: # This operand slot is not used
                        continue

                    # Check for direct call targets
                    if op.type == ida_ua.o_near or op.type == ida_ua.o_far:
                        target_addr = op.addr
                        target_func = ida_funcs.get_func(target_addr)
                        if target_func:
                            target_name = ida_funcs.get_func_name(target_addr)
                            if not target_name: target_name = f"sub_{target_addr:X}"
                            if target_name in call_count:
                                call_count[target_name] += 1
                            else:
                                call_count[target_name] = 1
                                called_funcs.append((target_name, target_addr))
                            break # Found target for this call instruction, move to next instruction

                    # Check for potential indirect call targets via memory reference
                    # This is a simplification. True static resolution of indirect calls is hard.
                    elif op.type == ida_ua.o_mem and op.addr != 0:
                        # This checks if the operand's address *itself* is the start of a function.
                        # This is more likely for calls like `call ds:dword_XXXX` where dword_XXXX is a function pointer.
                        target_func_at_op_addr = ida_funcs.get_func(op.addr)
                        if target_func_at_op_addr and target_func_at_op_addr.start_ea == op.addr:
                            target_name = ida_funcs.get_func_name(op.addr)
                            if not target_name: target_name = f"sub_{op.addr:X}"
                            if target_name in call_count:
                                call_count[target_name] += 1
                            else:
                                call_count[target_name] = 1
                                called_funcs.append((target_name, op.addr))
                            break # Found target

    if not lite:
        try:
            # FlowChart analysis can be slow and sometimes less reliable for calls.
            # For now, we'll skip it in the 'lite' version of this example.
            # If you need it, it would go here.
            # Example:
            # flowchart = idaapi.FlowChart(func)
            # for block in flowchart:
            #     # Logic to inspect block for calls
            pass
        except Exception as e:
            print(f"[DEBUG] FlowChart analysis skipped or failed for {hex(func_ea)}: {e}")

    # Method 2: CodeRefsFrom (good for direct calls and some indirect ones resolved by IDA)
    # This often catches what is_call_insn + operand analysis might miss if IDA has
    # already determined a code reference.
    for instr_addr_cref in idautils.FuncItems(func.start_ea): # Renamed variable
        # Check if the instruction itself is a call to be more targeted,
        # though CodeRefsFrom on any instruction *could* point to a function.
        # if idaapi.is_call_insn(instr_addr_cref): # Optional: be more restrictive
        for xref_target_ea in idautils.CodeRefsFrom(instr_addr_cref, 1): # flow=1 means only code refs
            if xref_target_ea != ida_idaapi.BADADDR:
                target_func_cref = ida_funcs.get_func(xref_target_ea) # Renamed variable
                if target_func_cref and target_func_cref.start_ea != func.start_ea: # Is a function and not self
                    target_name_cref = ida_funcs.get_func_name(target_func_cref.start_ea) # Renamed
                    if not target_name_cref: target_name_cref = f"sub_{target_func_cref.start_ea:X}"

                    # Check if already added by the first method to avoid duplicate entries in called_funcs
                    # but still increment count.
                    is_new_entry = True
                    for existing_name, existing_addr in called_funcs:
                        if existing_addr == target_func_cref.start_ea:
                            is_new_entry = False
                            break
                    
                    if target_name_cref in call_count:
                        call_count[target_name_cref] += 1
                    else:
                        call_count[target_name_cref] = 1
                    
                    if is_new_entry:
                        called_funcs.append((target_name_cref, target_func_cref.start_ea))


    # Final deduplication of the `called_funcs` list while preserving accurate counts from `call_count`.
    # The `call_count` dictionary should be the source of truth for counts.
    # The `called_funcs` list should just be unique (name, addr) pairs.
    final_called_funcs_list = []
    seen_func_addrs = set()
    for name, addr in called_funcs:
        if addr not in seen_func_addrs:
            # Get the potentially updated name if IDA changed it during analysis
            current_name_for_addr = ida_funcs.get_func_name(addr)
            if not current_name_for_addr: current_name_for_addr = f"sub_{addr:X}"
            
            # Ensure the name used in final_called_funcs_list matches one in call_count_dict
            # This handles cases where a function might be found with a default name then a real name.
            # For simplicity, we'll use the name from the first encounter, but counts are from call_count_dict.
            # A more robust way would be to always use addr as the key for counts internally.

            # Use the name that's likely in call_count_dict. If multiple names point to same addr,
            # this can get tricky. We'll use the name from the `called_funcs` list.
            final_called_funcs_list.append((name, addr))
            seen_func_addrs.add(addr)

    # Ensure call_count_dict accurately reflects counts for unique functions
    # This step might be redundant if call_count_dict is built correctly above.
    # For simplicity, we assume call_count_dict is already correct.

    # print(f"[DEBUG] Enhanced detection found {len(final_called_funcs_list)} unique called functions for {hex(func_ea)}")
    return final_called_funcs_list, call_count 
def get_function_assembly(func_ea):
    """Get the assembly instructions for a function."""
    func = idaapi.get_func(func_ea)
    if not func:
        return "No function found at this address."
    
    assembly = []
    for instr_addr in idautils.FuncItems(func.start_ea):
        disasm = idc.generate_disasm_line(instr_addr, 0)
        line = f"{hex(instr_addr)}: {disasm}"
        assembly.append(line)
    
    return "\n".join(assembly)

def get_function_classrefs(func_ea):
    """Get Objective-C class references used in the function."""
    func = idaapi.get_func(func_ea)
    if not func:
        return []
    
    classrefs = []
    for instr_addr in idautils.FuncItems(func.start_ea):
        for xref in idautils.XrefsFrom(instr_addr, 0):
            # Check if it points to a valid address
            if xref.to != ida_idaapi.BADADDR:
                # Try to get symbolic name
                name = ida_name.get_name(xref.to)
                if name and ("_OBJC_CLASS_$_" in name or "_OBJC_METACLASS_$_" in name):
                    class_name = name.replace("_OBJC_CLASS_$_", "").replace("_OBJC_METACLASS_$_", "")
                    classrefs.append((class_name, hex(xref.to)))
    
    return classrefs
def get_function_context(function_addr,
                         include_called_functions=True, max_funcs=5,
                         include_callers=True, max_callers=5,
                         include_strings=True, include_data_refs=True,
                         include_xrefs_from=True,
                         decompile_neighbors=True,
                         lite_mode=False,
                         lite_mode_caller_callee_aware=True,
                         include_assembly=False,    # New parameter for assembly
                         include_classrefs=True):

    func = idaapi.get_func(function_addr)
    if not func:
        return "No function context available (or not a function)"

    current_func_name = idaapi.get_func_name(func.start_ea)
    if not current_func_name: current_func_name = f"sub_{func.start_ea:X}" # Ensure name
    context = f"Function: {current_func_name} at {hex(func.start_ea)}\n"
    context += f"Size: {func.end_ea - func.start_ea} bytes\n\n"

    # --- Determine Effective Settings Based on Modes ---
    effective_include_strings = include_strings
    effective_include_data_refs = include_data_refs
    effective_include_xrefs_from = include_xrefs_from
    effective_decompile_neighbors = decompile_neighbors
    # Limits for how many *names* of callers/callees to list in the context string
    effective_max_names_listed_callees = max_funcs
    effective_max_names_listed_callers = max_callers
    # Limits for how many *decompilations* of callers/callees to include
    effective_max_decompilations_callees = max_funcs
    effective_max_decompilations_callers = max_callers
    effective_include_assembly = include_assembly     # New variable
    effective_include_classrefs = include_classrefs   

    # This is for the very slow enhanced caller search via string name matching
    run_enhanced_caller_search_via_strings = False # Default to OFF for speed

    if lite_mode: # The most aggressive lite mode
        effective_include_strings = False
        effective_include_data_refs = False
        effective_include_xrefs_from = False
        effective_decompile_neighbors = False
        effective_max_names_listed_callees = min(max_funcs, 1) # List fewer names
        effective_max_names_listed_callers = min(max_callers, 1) # List fewer names
        run_enhanced_caller_search_via_strings = False
        effective_include_assembly = False   # Always include assembly in lite mode
        effective_include_classrefs = True 
    elif lite_mode_caller_callee_aware: # Targeted lite mode for caller/callee names
        effective_include_strings = True
        effective_include_data_refs = True
        effective_include_xrefs_from = True
        effective_decompile_neighbors = True # CRITICAL: No decompilation of neighbors
        # Keep original max_funcs/max_callers for name listing, or set a specific moderate number
        effective_max_names_listed_callees = min(max_funcs, 5) # e.g., list up to 5 callee names
        effective_max_names_listed_callers = min(max_callers, 5) # e.g., list up to 5 caller names
        run_enhanced_caller_search_via_strings = False
        effective_include_assembly = False   # Always include assembly in lite mode
        effective_include_classrefs = True 
    # Debug print for effective settings
    print(f"[DEBUG] Context for {hex(function_addr)} - Lite: {lite_mode}, LiteAware: {lite_mode_caller_callee_aware}")
    print(f"[DEBUG]   effective_include_strings: {effective_include_strings}")
    print(f"[DEBUG]   effective_decompile_neighbors: {effective_decompile_neighbors}")
    print(f"[DEBUG]   run_enhanced_caller_search_via_strings: {run_enhanced_caller_search_via_strings}")


    # --- Collect Called Functions (Names & Counts) ---
    called_funcs_list, call_count_dict = [], {} # Renamed to avoid scope issues
    if include_called_functions: # Check the original parameter before fetching
        # Pass the appropriate lite flag to get_enhanced_called_functions if it supports it
        is_lite_for_get_enhanced = lite_mode or lite_mode_caller_callee_aware
        print(f"[DEBUG] Looking for functions called by {hex(function_addr)} (lite for get_enhanced: {is_lite_for_get_enhanced})")
        called_funcs_list, call_count_dict = get_enhanced_called_functions(function_addr, lite=is_lite_for_get_enhanced)
        print(f"[DEBUG] Found {len(called_funcs_list)} functions called by {hex(function_addr)}")


    # --- Collect Caller Functions (Names) ---
    caller_funcs_list = [] # Renamed
    if include_callers: # Check the original parameter before fetching
        print(f"[DEBUG] Looking for functions that call {hex(function_addr)}")
        # Standard xrefs detection (efficient)
        for xref in idautils.XrefsTo(func.start_ea, 0): # Only direct code refs to function start
            if xref.type == ida_xref.fl_CN or xref.type == ida_xref.fl_CF: # Call Near, Call Far
                caller_func_obj = ida_funcs.get_func(xref.frm) # Use a different var name
                # Check if xref.frm is within a function and is a call instruction
                if caller_func_obj and idaapi.is_call_insn(xref.frm):
                    caller_name_str = ida_funcs.get_func_name(caller_func_obj.start_ea) # Renamed
                    if not caller_name_str: caller_name_str = f"sub_{caller_func_obj.start_ea:X}"
                    caller_funcs_list.append((caller_name_str, caller_func_obj.start_ea))

        # Enhanced caller search via string name matching (VERY SLOW - controlled by flag)
        if run_enhanced_caller_search_via_strings:
            print(f"[DEBUG] Running SLOW enhanced caller detection (string search) for {current_func_name}")
            # This loop is extremely performance intensive. Use with extreme caution.
            for seg_idx in range(ida_segment.get_segm_qty()):
                seg = ida_segment.getnseg(seg_idx)
                if seg:
                    for ea_in_seg in idautils.Functions(seg.start_ea, seg.end_ea): # Renamed var
                        if ea_in_seg == func.start_ea: continue # Don't include self

                        potential_caller_func = ida_funcs.get_func(ea_in_seg)
                        if potential_caller_func:
                            # Optimization: check only a few key places or if function names suggest relationship
                            # For now, full iteration as per original logic if enabled
                            found_in_this_caller = False
                            for item_ea in idautils.FuncItems(potential_caller_func.start_ea):
                                for xref_from_item in idautils.XrefsFrom(item_ea, 0):
                                    if xref_from_item.to != ida_idaapi.BADADDR:
                                        # Check if xref_from_item.to is a string
                                        str_info = ida_bytes.get_strlit_contents(xref_from_item.to, -1, ida_nalt.STRTYPE_C)
                                        if str_info:
                                            str_content_val = ""
                                            if isinstance(str_info, bytes):
                                                try: str_content_val = str_info.decode('utf-8', errors='replace')
                                                except: str_content_val = str(str_info)
                                            else: str_content_val = str(str_info)

                                            if current_func_name in str_content_val: # current_func_name is defined at the start
                                                caller_name_str = ida_funcs.get_func_name(potential_caller_func.start_ea)
                                                if not caller_name_str: caller_name_str = f"sub_{potential_caller_func.start_ea:X}"
                                                caller_funcs_list.append((caller_name_str, potential_caller_func.start_ea))
                                                found_in_this_caller = True
                                                break # Found ref in this item, move to next item
                                if found_in_this_caller: break # Found ref in this potential_caller, move to next potential_caller
                            # if found_in_this_caller: continue # To next ea_in_seg (already handled by break)


        # Deduplicate caller_funcs_list
        unique_caller_funcs_list = []
        seen_caller_names = set()
        for name, addr in caller_funcs_list:
            if name not in seen_caller_names: # Could also use (name, addr) for stricter uniqueness if needed
                seen_caller_names.add(name)
                unique_caller_funcs_list.append((name, addr))
        caller_funcs_list = unique_caller_funcs_list
        print(f"[DEBUG] Found {len(caller_funcs_list)} unique caller functions for {hex(function_addr)}")


    # --- Collect Strings, Data Refs, Xrefs From (based on effective settings) ---
    string_refs_list = []
    if effective_include_strings:
        print(f"[DEBUG] Collecting string references for {hex(function_addr)}")
        for instr_addr_str in idautils.FuncItems(func.start_ea): # Renamed
            # XrefsFrom can be slow if a function has many instructions.
            # Consider limiting how many items we check or types of xrefs.
            for xref_str in idautils.XrefsFrom(instr_addr_str, 0):
                # Check if xref_str.to points to a string literal
                # ida_bytes.is_strlit(ida_bytes.get_flags(xref_str.to))
                # xref.type 1 and 2 are often dr_O (offset) or dr_W (write), dr_R (read) which can point to strings
                # A more precise check is get_strlit_contents itself
                possible_str_content = ida_bytes.get_strlit_contents(xref_str.to, -1, ida_nalt.STRTYPE_C)
                if possible_str_content is None:
                     possible_str_content = ida_bytes.get_strlit_contents(xref_str.to, -1, ida_nalt.STRTYPE_TERMCHR)

                if possible_str_content:
                    str_val = "" # Renamed
                    if isinstance(possible_str_content, bytes):
                        try: str_val = possible_str_content.decode('utf-8', errors='replace')
                        except: str_val = str(possible_str_content)
                    else: str_val = str(possible_str_content)

                    if "li.txt" in str_val or "bi.txt" in str_val or "config-encrypt.txt" in str_val:
                        string_refs_list.append(f"[IMPORTANT CONFIG FILE] {str_val}")
                    else:
                        string_refs_list.append(str_val)
        print(f"[DEBUG] Found {len(string_refs_list)} string references.")


    data_refs_list = []
    if effective_include_data_refs:
        print(f"[DEBUG] Collecting data references for {hex(function_addr)}")
        for instr_addr_data in idautils.FuncItems(func.start_ea): # Renamed
            for xref_data in idautils.XrefsFrom(instr_addr_data, 0):
                # Skip if it's a string we already recorded or if it's code
                if ida_bytes.get_strlit_contents(xref_data.to, -1, ida_nalt.STRTYPE_C): # STRTYPE_ANY checks for any known string type
                    continue
                if ida_bytes.is_code(ida_bytes.get_flags(xref_data.to)):
                    continue

                # Try to get symbolic name for data
                data_name_str = ida_name.get_ea_name(xref_data.to) # Renamed
                # Heuristic: meaningful data names often don't start with default IDA prefixes
                # and are not just addresses.
                if data_name_str and not data_name_str.startswith("loc_") and \
                   not data_name_str.startswith("byte_") and \
                   not data_name_str.startswith("word_") and \
                   not data_name_str.startswith("dword_") and \
                   not data_name_str.startswith("qword_") and \
                   not data_name_str.startswith("unk_"):
                    tif = ida_typeinf.tinfo_t()
                    if ida_nalt.get_tinfo(tif, xref_data.to): # Check if type info exists
                        type_name_str = tif.dstr() # dstr() gives a printable type string
                        if type_name_str:
                             data_refs_list.append(f"{data_name_str} (Type: {type_name_str}) @ {hex(xref_data.to)}")
                        else:
                             data_refs_list.append(f"{data_name_str} @ {hex(xref_data.to)}")
                    else:
                        data_refs_list.append(f"{data_name_str} @ {hex(xref_data.to)}")
                # Optionally, add unnamed data xrefs if they have types
                else:
                    tif = ida_typeinf.tinfo_t()
                    if ida_nalt.get_tinfo(tif, xref_data.to):
                       type_name_str = tif.dstr()
                       if type_name_str and type_name_str != "void" and type_name_str != "unknown":
                          data_refs_list.append(f"Unnamed_data_{hex(xref_data.to)} (Type: {type_name_str})")

        print(f"[DEBUG] Found {len(data_refs_list)} data references.")


    xrefs_from_current_func_list = []
    if effective_include_xrefs_from:
        print(f"[DEBUG] Collecting general XRefs FROM {hex(function_addr)}")
        xrefs_from_current_func_list = get_function_xrefs_from(function_addr) # Already defined
        print(f"[DEBUG] Found {len(xrefs_from_current_func_list)} general XRefs FROM.")


    # --- Build Context String ---
    # (Function name and size already added)

    # Add Callers (Names Only, limited by effective_max_names_listed_callers)
    if include_callers: # Based on original intent to include caller info
        if caller_funcs_list:
            context += "Called by:\n"
            for name, addr in caller_funcs_list[:effective_max_names_listed_callers]:
                context += f"- {name} ({hex(addr)})\n"
            if len(caller_funcs_list) > effective_max_names_listed_callers:
                context += f"  ... and {len(caller_funcs_list) - effective_max_names_listed_callers} more caller functions\n"
        else: # caller_funcs_list is empty
            context += "This function has no callers found by standard xrefs.\n"
            if run_enhanced_caller_search_via_strings: # If the slow search was enabled and found nothing
                context += "(Enhanced string search for callers also yielded no results).\n"
    context += "\n" # Add a newline for separation

    # Add Callees (Names and Counts Only, limited by effective_max_names_listed_callees)
    if include_called_functions: # Based on original intent to include callee info
        if called_funcs_list:
            context += "Calls:\n"
            # Sort by call frequency for name listing if not already sorted by get_enhanced_called_functions
            # Assuming get_enhanced_called_functions doesn't sort by count, or we want to be sure.
            display_callees_sorted = sorted(
                called_funcs_list, # Use the collected list
                key=lambda x_item: call_count_dict.get(x_item[0], 0),
                reverse=True
            )
            for name, addr in display_callees_sorted[:effective_max_names_listed_callees]:
                call_times = call_count_dict.get(name, 1)
                call_str = "once" if call_times == 1 else f"{call_times} times"
                context += f"- {name} ({hex(addr)}) - called {call_str}\n"
            if len(called_funcs_list) > effective_max_names_listed_callees:
                context += f"  ... and {len(called_funcs_list) - effective_max_names_listed_callees} more called functions\n"
        else: # called_funcs_list is empty
            context += "This function doesn't call any other functions.\n"
    context += "\n" # Add a newline for separation


    # Add String References (if collected and not empty)
    # Add String References (if collected and not empty)
    if string_refs_list:
        context += "String references:\n"
        limit_displayed_strings = 20 # Configurable limit
        for s_idx, s_val in enumerate(string_refs_list):
            if s_idx >= limit_displayed_strings:
                context += f"  ... and {len(string_refs_list) - limit_displayed_strings} more string references\n"
                break
            truncated_s_val = s_val
            if len(s_val) > 100: truncated_s_val = s_val[:100] + "..."
            context += f"- \"{truncated_s_val}\"\n"
        context += "\n"


    # Add Data References (if collected and not empty)
    if data_refs_list:
        context += "Data references:\n"
        limit_displayed_data_refs = 15 # Configurable limit
        for dr_idx, dr_val in enumerate(data_refs_list):
            if dr_idx >= limit_displayed_data_refs:
                context += f"  ... and {len(data_refs_list) - limit_displayed_data_refs} more data references\n"
                break
            context += f"- {dr_val}\n"
        context += "\n"


    # Add General Xrefs From (if collected and not empty)
    if xrefs_from_current_func_list:
        code_xrefs_from = [x for x in xrefs_from_current_func_list if x["type"] == "Code"]
        data_xrefs_from = [x for x in xrefs_from_current_func_list if x["type"] == "Data" or x["type"] == "String"]

        if code_xrefs_from:
            context += "Code references FROM this function (first 10):\n"
            for xref_item_code in code_xrefs_from[:10]:
                context += f"- {xref_item_code['name']} ({hex(xref_item_code['address'])})\n"
            if len(code_xrefs_from) > 10:
                context += f"  ... and {len(code_xrefs_from) - 10} more code references FROM this function\n"
            context += "\n"

        if data_xrefs_from:
            context += "Data/String references FROM this function (first 10):\n"
            for xref_item_data in data_xrefs_from[:10]:
                if xref_item_data["string_content"]:
                    context += f"- {xref_item_data['name']} ({hex(xref_item_data['address'])}) = \"{xref_item_data['string_content'][:50]}\"\n"
                else:
                    context += f"- {xref_item_data['name']} ({hex(xref_item_data['address'])})\n"
            if len(data_xrefs_from) > 10:
                context += f"  ... and {len(data_xrefs_from) - 10} more data/string references FROM this function\n"
            context += "\n"

    # Add Assembly if enabled
    if effective_include_assembly:
        assembly_code = get_function_assembly(function_addr)
        context += "Assembly code for this function:\n"
        context += assembly_code
        context += "\n\n"
        
        # Also include assembly for callers if available
        if include_callers and caller_funcs_list:
            for name, addr in caller_funcs_list[:effective_max_names_listed_callers]:
                caller_assembly = get_function_assembly(addr)
                context += f"Assembly for caller {name} ({hex(addr)}):\n"
                context += caller_assembly
                context += "\n\n"
    
    # Add Classrefs if enabled and there are any found
    if effective_include_classrefs:
        classrefs = get_function_classrefs(function_addr)
        if classrefs:
            context += "Objective-C Class References in this function:\n"
            for class_name, addr in classrefs:
                context += f"- {class_name} ({addr})\n"
            context += "\n"
            
            # Also include classrefs for callers
            if include_callers and caller_funcs_list:
                for name, addr in caller_funcs_list[:effective_max_names_listed_callers]:
                    caller_classrefs = get_function_classrefs(addr)
                    if caller_classrefs:
                        context += f"Objective-C Class References in caller {name}:\n"
                        for class_name, class_addr in caller_classrefs:
                            context += f"- {class_name} ({class_addr})\n"
                        context += "\n"

    # Decompiled Neighbors (ONLY if effective_decompile_neighbors is True)
    if effective_decompile_neighbors:
        # Decompile Callers
        if include_callers and caller_funcs_list: # Check original intent and if any callers found
            # Use effective_max_decompilations_callers to limit how many are decompiled
            callers_to_decompile = caller_funcs_list[:effective_max_decompilations_callers]
            if callers_to_decompile:
                context += "\nDecompiled code of functions that call this function:\n"
                for name, addr in callers_to_decompile:
                    print(f"[DEBUG] Decompiling caller: {name} at {hex(addr)}")
                    code = decompile_function(addr)
                    if code:
                        context += f"\n--- Caller: {name} ({hex(addr)}) ---\n{textwrap.shorten(code, width=2000, placeholder='...(code too long)...')}\n--- End of {name} ---\n"
                    else:
                        context += f"\n--- Caller: {name} ({hex(addr)}) (decompilation failed) ---\n"

        # Decompile Callees
        if include_called_functions and called_funcs_list: # Check original intent and if any callees found
            # Sort by call frequency before selecting which ones to decompile
            sorted_callees_for_decomp = sorted(
                called_funcs_list,
                key=lambda x_item: call_count_dict.get(x_item[0], 0),
                reverse=True
            )
            # Use effective_max_decompilations_callees to limit
            callees_to_decompile = sorted_callees_for_decomp[:effective_max_decompilations_callees]
            if callees_to_decompile:
                context += "\nDecompiled code of called functions (most frequent first):\n"
                for name, addr in callees_to_decompile:
                    print(f"[DEBUG] Decompiling callee: {name} at {hex(addr)}")
                    code = decompile_function(addr)
                    if code:
                        call_times = call_count_dict.get(name, 1)
                        call_str = "once" if call_times == 1 else f"{call_times} times"
                        context += f"\n--- Callee: {name} ({hex(addr)}) (called {call_str}) ---\n{textwrap.shorten(code, width=2000, placeholder='...(code too long)...')}\n--- End of {name} ---\n"
                    else:
                        context += f"\n--- Callee: {name} ({hex(addr)}) (decompilation failed) ---\n"

                # If more callees existed than were decompiled
                if len(called_funcs_list) > len(callees_to_decompile) and len(callees_to_decompile) > 0:
                    context += f"\n(Showing decompilation for {len(callees_to_decompile)} out of {len(called_funcs_list)} called functions)\n"
    else: # effective_decompile_neighbors is False
        if (include_callers and caller_funcs_list) or \
           (include_called_functions and called_funcs_list):
            context += "\n(Decompilation of neighboring functions was skipped for speed based on current mode).\n"
    print(f"[DEBUG] Total context size: {len(context)} characters")
    print(f"[DEBUG] Does context include assembly? {'Assembly code for this function' in context}")
    print(f"[DEBUG] Does context include classrefs? {'Class References' in context}")
    return context


def get_binary_info():

    info = {}

    # Get binary name using idc which is more stable across versions
    info["filename"] = idc.get_root_filename()

    # Get architecture information using ida_ida instead of idc
    proc_name = ida_ida.inf_get_procname()
    # Handle both string and bytes cases to ensure compatibility
    if isinstance(proc_name, bytes):
        info["processor"] = proc_name.decode('utf-8')
    else:
        info["processor"] = proc_name

    # Use ida_ida for bitness information instead of idc.INF_IS_64BIT
    info["bitness"] = "64-bit" if ida_ida.inf_is_64bit() else "32-bit"

    # Check if it's likely an iOS binary by looking at file extension and segments
    is_ios = False

    # Check file extension
    file_ext = os.path.splitext(info["filename"])[1].lower()
    if file_ext in [".dylib", ".framework"]:
        is_ios = True
    else:
        # Look for Objective-C segments
        for seg_idx in range(ida_segment.get_segm_qty()):
            seg = ida_segment.getnseg(seg_idx)
            if seg:
                seg_name = ida_segment.get_segm_name(seg)
                if "__OBJC" in seg_name:
                    is_ios = True
                    break

    info["is_ios"] = is_ios

    return info


# Function to detect if function is likely a thunk, nullsub, or break function
def is_special_function(func_ea):

    func = idaapi.get_func(func_ea)
    if not func:
        return True, "Unknown function"

    if func.end_ea - func.start_ea < 32:
        # Check for specific patterns in decompiled code
        try:
            cfunc = ida_hexrays.decompile(func_ea)
            if cfunc:
                code = str(cfunc)
                # Check if it's a break function
                if re.search(r'{\s*__break\(.*\);\s*}', code):
                    return True, "Break function"

                # Check if it's a nullsub
                if re.search(r'{\s*;\s*}', code):
                    return True, "Nullsub function"

                # Check if it's a thunk
                if re.search(r'{\s*return\s+[a-zA-Z0-9_]+\(.*\);\s*}', code):
                    return True, "Thunk function"

                # Check if it's a constant return
                if re.search(r'{\s*return\s+([0-9]+|0x[0-9a-fA-F]+)(?:LL|ULL)?;\s*}', code):
                    return True, "Constant return function"
        except:
            pass

    return False, None


# Function to get call chain
def get_call_chain(function_addr, max_depth=2, include_callees=False):
    """
    Get functions in both directions of the call chain:
    - Callers: functions that call the current function (reverse call chain)
    - Callees: functions that are called by the current function (forward call chain)
    
    Returns a list of function addresses to analyze
    """
    # Start with the current function
    queue = [function_addr]
    visited = set([function_addr])
    result = [function_addr]
    depth = 0
    
    # Track direction for each item in the queue (True = forward/callees, False = reverse/callers)
    # Start with both directions if include_callees is True
    directions = [True, False] if include_callees else [False]
    direction_queue = [(function_addr, direction) for direction in directions]
    
    while direction_queue and depth < max_depth:
        depth += 1
        level_size = len(direction_queue)
        
        for _ in range(level_size):
            current, is_forward = direction_queue.pop(0)
            
            if is_forward:
                # Forward direction: Get functions called by this function
                called_funcs, _ = get_enhanced_called_functions(current)
                for name, callee_addr in called_funcs:
                    # Check if the function is special (thunk, nullsub, etc.)
                    is_special, _ = is_special_function(callee_addr)
                    if not is_special and callee_addr not in visited:
                        visited.add(callee_addr)
                        direction_queue.append((callee_addr, True))  # Continue in forward direction
                        result.append(callee_addr)
            else:
                # Reverse direction: Get functions that call this function
                for xref in idautils.XrefsTo(current, 0):
                    caller = idaapi.get_func(xref.frm)
                    if caller and idaapi.is_call_insn(xref.frm):
                        caller_addr = caller.start_ea
                        
                        # Check if the function is special (thunk, nullsub, etc.)
                        is_special, _ = is_special_function(caller_addr)
                        if not is_special and caller_addr not in visited:
                            visited.add(caller_addr)
                            direction_queue.append((caller_addr, False))  # Continue in reverse direction
                            result.append(caller_addr)
    
    print(f"[DEBUG] Found {len(result)} functions in the bidirectional call chain")
    return result

class VulChatPlugin(idaapi.plugin_t):
    flags = 0
    # Only keep the analyze and rename action
    analyze_action_name = "vulchat:analyze_function"
    analyze_chain_action_name = "vulchat:analyze_call_chain" 
    analyze_visible_action_name = "vulchat:analyze_visible_functions"    # New action name
    analyze_visible_menu_path = "Edit/VulChat/Analyze All Visible Functions"
    analyze_menu_path = "Edit/VulChat/Analyze and Rename Function"
    analyze_chain_menu_path = "Edit/VulChat/Analyze Call Chain"  # New menu path
    wanted_name = 'VulChat'
    wanted_hotkey = ''
    comment = "Uses OpenRouter to analyze decompiler's output"
    help = "See usage instructions on GitHub"
    menu = None

    def init(self):
        # Check whether the decompiler is available
        if not ida_hexrays.init_hexrays_plugin():
            return idaapi.PLUGIN_SKIP

        # Check if OpenRouter API key is set
        if not OPENROUTER_API_KEY:
            openrouter_key = os.getenv("OPENROUTER_API_KEY")
            if not openrouter_key:
                print("Please edit this script to insert your OpenRouter API key!")
                return idaapi.PLUGIN_SKIP
            globals()["OPENROUTER_API_KEY"] = openrouter_key

        # Analyze action for analysis and renaming
        analyze_action = idaapi.action_desc_t(self.analyze_action_name,
                                              'Analyze and Rename Function',
                                              AnalyzeHandler(),
                                              "Ctrl+Alt+A",
                                              'Use OpenRouter to analyze, explain and rename function variables',
                                              199)
        idaapi.register_action(analyze_action)
        idaapi.attach_action_to_menu(self.analyze_menu_path, self.analyze_action_name, idaapi.SETMENU_APP)

        # New action for analyzing the call chain
        analyze_chain_action = idaapi.action_desc_t(self.analyze_chain_action_name,
                                                'Analyze Call Chain',
                                                AnalyzeChainHandler(),
                                                "Ctrl+Alt+C",
                                                'Systematically analyze all functions in call chain',
                                                199)
        idaapi.register_action(analyze_chain_action)
        idaapi.attach_action_to_menu(self.analyze_chain_menu_path, self.analyze_chain_action_name, idaapi.SETMENU_APP)
        analyze_visible_action = idaapi.action_desc_t(
            self.analyze_visible_action_name,
            'Analyze All Visible Functions',
            AnalyzeVisibleHandler(),
            "Ctrl+Alt+V",
            'Analyze all functions visible in current pseudocode',
            199
        )
        idaapi.register_action(analyze_visible_action)
        idaapi.attach_action_to_menu(
            self.analyze_visible_menu_path, 
            self.analyze_visible_action_name, 
            idaapi.SETMENU_APP
        )

        # Register context menu actions
        self.menu = ContextMenuHooks()
        self.menu.hook()

        return idaapi.PLUGIN_KEEP

    def run(self, arg):
        pass

    def term(self):
        idaapi.detach_action_from_menu(self.analyze_menu_path, self.analyze_action_name)
        idaapi.detach_action_from_menu(self.analyze_chain_menu_path, self.analyze_chain_action_name)
        idaapi.detach_action_from_menu(self.analyze_visible_menu_path, self.analyze_visible_action_name)
        
        if self.menu:
            self.menu.unhook()
        return


# -----------------------------------------------------------------------------

class ContextMenuHooks(idaapi.UI_Hooks):
    def finish_populating_widget_popup(self, form, popup):
        # Add actions to the context menu of the Pseudocode view
        if idaapi.get_widget_type(form) == idaapi.BWN_PSEUDOCODE:
            idaapi.attach_action_to_popup(form, popup, VulChatPlugin.analyze_action_name, "VulChat/")
            idaapi.attach_action_to_popup(form, popup, VulChatPlugin.analyze_chain_action_name, "VulChat/")
            idaapi.attach_action_to_popup(form, popup, VulChatPlugin.analyze_visible_action_name, "VulChat/")


# -----------------------------------------------------------------------------
class AnalyzeVisibleHandler(idaapi.action_handler_t):
    def __init__(self):
        idaapi.action_handler_t.__init__(self)

    def activate(self, ctx):
        v = ida_hexrays.get_widget_vdui(ctx.widget)
        if not v:
            print("No pseudocode view available")
            return 0

        visible_funcs = self.get_visible_functions(v)
        if not visible_funcs:
            print("No functions found in pseudocode view")
            return 0

        # Format function list for display
        func_names = []
        for addr in visible_funcs:
            name = ida_name.get_ea_name(addr)
            if not name:
                name = f"sub_{hex(addr)[2:]}"
            func_names.append(f"{name} at {hex(addr)}")
        
        func_list = "\n".join([f"{i+1}. {name}" for i, name in enumerate(func_names)])
        
        confirm = ida_kernwin.ask_yn(
            ida_kernwin.ASKBTN_YES,
            f"Found {len(visible_funcs)} functions in the current view:\n\n{func_list}\n\nProceed with analysis?"
        )
        
        if confirm != ida_kernwin.ASKBTN_YES:
            return 0

        self.analyze_functions(visible_funcs)
        return 1

    def get_visible_functions(self, v):
        visible_funcs = set()
        
        if v.cfunc:
            # Add the main function
            visible_funcs.add(v.cfunc.entry_ea)
            
            # Get all instructions in the function
            func = idaapi.get_func(v.cfunc.entry_ea)
            if func:
                for instr_addr in idautils.FuncItems(func.start_ea):
                    if idaapi.is_call_insn(instr_addr):
                        for xref in idautils.XrefsFrom(instr_addr, 0):
                            if xref.type in [ida_xref.fl_CN, ida_xref.fl_CF]:
                                target_func = ida_funcs.get_func(xref.to)
                                if target_func:
                                    visible_funcs.add(target_func.start_ea)

        return list(visible_funcs)

    def analyze_functions(self, function_addrs):
        total = len(function_addrs)
        print(f"Starting analysis of {total} visible functions...")
        
        # Show progress dialog
        ida_kernwin.show_wait_box(f"Analyzing {total} functions...")
        
        try:
            for i, addr in enumerate(function_addrs):
                ida_kernwin.replace_wait_box(f"Analyzing function {i+1}/{total}: {hex(addr)}")
                
                try:
                    current_func = ida_hexrays.decompile(addr)
                    if not current_func:
                        print(f"Could not decompile function at {hex(addr)}, skipping...")
                        continue
                    
                    func_context = get_function_context(
                        addr,
                        include_called_functions=True,
                        max_funcs=5,
                        include_callers=True,
                        max_callers=5,
                        include_strings=True,
                        include_data_refs=True,
                        include_assembly=False,    # Include assembly
                        include_classrefs=True    # Include classrefs
                    )
                    
                    binary_info = get_binary_info()
                    func_size = len(str(current_func))
                    
                    # Create prompt based on function size
                    if func_size > 400000:
                        prompt = f"""Analyze the following decompiled pseudocode from IDA Pro. 

This is a LARGE FUNCTION. Please focus on core functionality only.

Function Context:
{func_context}

Decompiled Pseudocode (IDA Pro):
{str(current_func)}

IMPORTANT: Respond ONLY with a valid JSON object that strictly follows this format:
{{
  "comment": "Brief explanation of the core functionality based on the actual code logic and its calling context",
  "function_name": "suggestedFunctionName",
  "variables": [
    {{"original_name": "v1", "new_name": "betterName"}},
    {{"original_name": "a1", "new_name": "betterName"}}
  ],
  "security_role": ""
}}"""
                    else:
                        prompt = f"""Analyze the following pseudocode from IDA Pro.

Binary Information:
{binary_info}

Function Context:
{func_context}

Decompiled Pseudocode (IDA Pro):
{str(current_func)}

IMPORTANT: Your response MUST be a valid JSON object following this format:
{{
  "comment": "Explanation of what the function does based on code analysis and context",
  "function_name": "descriptiveName",
  "variables": [
    {{"original_name": "v1", "new_name": "betterName"}},
    {{"original_name": "a1", "new_name": "betterName"}}
  ],
  "security_role": ""
}}"""

                    # Process the function synchronously
                    headers = {
                        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "http://localhost",
                    }

                    data = {
                        "model": OPENROUTER_MODEL,
                        "messages": [
                            {"role": "system", "content": "You are a helpful assistant specializing in code analysis, reverse engineering, and code improvement. ALWAYS provide your responses in valid JSON format as specified in the user's request."},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.4,
                        "max_tokens": 100000,
                        "top_p": 1,
                        "frequency_penalty": 1,
                        "presence_penalty": 1,
                        "response_format": {"type": "json_object"}
                    }

                    response = requests.post(
                        f"{OPENROUTER_BASE_URL}/chat/completions",
                        headers=headers,
                        json=data,
                        timeout=180
                    )

                    response_json = response.json()
                    
                    if 'error' in response_json:
                        print(f"API error for function {hex(addr)}: {response_json['error']}")
                        continue
                    
                    content = response_json['choices'][0]['message']['content']
                    result = None
                    
                    try:
                        result = json.loads(content)
                    except json.JSONDecodeError:
                        result = extract_components_from_text(content)
                    
                    if result:
                        apply_changes(result, current_func)
                    
                except Exception as e:
                    print(f"Error processing function at {hex(addr)}: {str(e)}")
                
        finally:
            ida_kernwin.hide_wait_box()

    def update(self, ctx):
        return idaapi.AST_ENABLE_ALWAYS
class AnalyzeHandler(idaapi.action_handler_t):
    """
    This handler analyzes and renames functions and variables
    """

    def __init__(self):
        idaapi.action_handler_t.__init__(self)

    def activate(self, ctx):
        function_addr = idaapi.get_screen_ea()
        current_func = ida_hexrays.decompile(function_addr)
        v = ida_hexrays.get_widget_vdui(ctx.widget)

        if not current_func:
            print("Could not decompile the current function")
            return 0

        # Check if it's a special function type that we shouldn't analyze
        is_special, special_type = is_special_function(function_addr)
        if is_special:
            print(f"This appears to be a {special_type}. These simple functions are typically not worth analyzing.")
            choice = ida_kernwin.ask_yn(ida_kernwin.ASKBTN_NO,
                                        f"This appears to be a {special_type}. Continue with analysis anyway?")
            if choice != ida_kernwin.ASKBTN_YES:
                return 0

        # Get enhanced function call context with more information and called functions
        func_context = get_function_context(
            function_addr,
            include_called_functions=True,
            max_funcs=5,
            include_callers=True,
            max_callers=5,
            include_strings=True,
            include_data_refs=True,
            include_assembly=False,    # Include assembly
            include_classrefs=True 
        )

        # Get basic binary info
        binary_info = get_binary_info()

        # Check function size and adjust analysis approach for large functions
        func_size = len(str(current_func))
        is_large_function = func_size > 400000  # Threshold for "large" function

        # Simplify prompt for large functions to improve JSON response success rate
        if is_large_function:
            print(f"Large function detected ({func_size} chars). Using simplified analysis approach.")

            # Simplified prompt for large functions
            prompt = f"""Analyze the following decompiled pseudocode from IDA Pro. 

This is a LARGE FUNCTION. Please focus on core functionality only.

Function Context:
{func_context}

Decompiled Pseudocode (IDA Pro):
{str(current_func)}

Analyze what this function actually does based on the code logic and its context. Pay close attention to:
1. What functions call this function (look at "Called by:" section)
2. What functions this function calls (look at "Calls:" section)
3. Any meaningful string or data references

The function's call graph context is essential for understanding its purpose. Look for patterns in the calling functions and called functions that could indicate its role. If caller functions are related to security, attestation, or protection, consider whether this function contributes to that functionality.

IMPORTANT: Respond ONLY with a valid JSON object that strictly follows this format:
{{
  "comment": "Brief explanation of the core functionality based on the actual code logic and its calling context",
  "function_name": "suggestedFunctionName",
  "variables": [
    {{"original_name": "v1", "new_name": "betterName"}},
    {{"original_name": "a1", "new_name": "betterName"}}
  ],
  "security_role": ""
}}

Rename as many variables as possible to make the code more readable - do not limit the number of renamed variables.
"""
        else:
            # Standard prompt for normal-sized functions
            prompt = f"""Analyze the following pseudocode from IDA Pro.

Binary Information:
- Filename: {binary_info["filename"]}
- Architecture: {binary_info["processor"]} {binary_info["bitness"]}
- iOS Binary: {"Yes" if binary_info["is_ios"] else "Likely not"}

Function Context:
{func_context}

Decompiled Pseudocode (IDA Pro):
{str(current_func)}

Please analyze this decompiled pseudocode thoroughly, considering:
1. The function's actual code logic
2. Functions that call this function (look at "Called by:" section)
3. Functions that this function calls (look at "Calls:" section)
4. Any string references or data references

Consider the relationships between this function and its callers/callees to determine its purpose. Function names of callers and callees can provide important clues about this function's purpose.

Provide:
1. A clear explanation of what this function does based on code logic and its calling context
2. A better function name that describes its purpose based on both operations and context
3. Better variable names to improve code readability (keeping in mind IDA Pro's naming conventions like v1, a1, etc.)
4. If the function analyzed contains control flow flattening techniques, try to figure out what each state might indicate, and what states might be indicicative of a failed check

IMPORTANT: Your response MUST be a valid JSON object following this format:
{{
  "comment": "Explanation of what the function does based on code analysis and context",
  "function_name": "descriptiveName",
  "variables": [
    {{"original_name": "v1", "new_name": "betterName"}},
    {{"original_name": "a1", "new_name": "betterName"}}
  ],
  "security_role": ""
}}

Fill in the security_role field ONLY if the function's relationship to security is ABSOLUTELY clear from its code or context.

DO NOT include any explanatory text outside of the JSON structure. Ensure your JSON is valid and properly formatted.
"""

        # Call the API asynchronously
        query_model_async(prompt, functools.partial(
            analyze_callback,
            current_func=current_func,
            view=v
        ))
        return 1

    # This action is always available
    def update(self, ctx):
        return idaapi.AST_ENABLE_ALWAYS


# -----------------------------------------------------------------------------

class AnalyzeChainHandler(idaapi.action_handler_t):
    """
    This handler analyzes all functions in the call chain
    """

    def __init__(self):
        idaapi.action_handler_t.__init__(self)

    def activate(self, ctx):
        function_addr = idaapi.get_screen_ea()
        
        # Ask user for chain depth
        max_depth = ida_kernwin.ask_long(3, "Maximum call chain depth (1-100):")
        if max_depth is None:
            return 0
        
        # Validate input
        max_depth = max(1, min(100, max_depth))
        
        # Get the call chain
        print(f"Building call chain for function at {hex(function_addr)}...")
        chain = get_call_chain(function_addr, max_depth)
        
        # Ask user for confirmation
        if len(chain) <= 1:
            ida_kernwin.warning(f"No additional functions found in call chain of {hex(function_addr)}")
            return 0
        
        func_names = [f"{idaapi.get_func_name(addr)} at {hex(addr)}" for addr in chain]
        func_list = "\n".join([f"{i+1}. {name}" for i, name in enumerate(func_names)])
        
        confirm = ida_kernwin.ask_yn(ida_kernwin.ASKBTN_YES, 
                                    f"Found {len(chain)} functions to analyze:\n\n{func_list}\n\nProceed with analysis?")
        
        if confirm != ida_kernwin.ASKBTN_YES:
            return 0
        # Process functions sequentially
        self.analyze_functions(chain)
        return 1
    
    def analyze_functions(self, function_addrs):
        """
        Process a list of functions sequentially
        """
        total = len(function_addrs)
        
        print(f"Starting analysis of {total} functions...")
        for i, addr in enumerate(function_addrs):
            print(f"\n[{i+1}/{total}] Analyzing function at {hex(addr)}...")
            
            try:
                # Decompile the function
                current_func = ida_hexrays.decompile(addr)
                if not current_func:
                    print(f"Could not decompile function at {hex(addr)}, skipping...")
                    continue
                
                # Get function context and other data, similar to AnalyzeHandler
                # Line 1709 (approximately)
                func_context = get_function_context(
                    addr,
                    include_called_functions=True,
                    max_funcs=5,
                    include_callers=True,
                    max_callers=5,
                    include_strings=True,
                    include_data_refs=True
                    # Missing include_assembly and include_classrefs
                )
                
                binary_info = get_binary_info()
                
                # Check function size
                func_size = len(str(current_func))
                is_large_function = func_size > 400000
                
                # Create prompt based on function size
                if is_large_function:
                    print(f"Large function detected ({func_size} chars). Using simplified analysis approach.")
                    prompt = self.create_large_function_prompt(func_context, current_func)
                else:
                    prompt = self.create_standard_prompt(binary_info, func_context, current_func)
                
                # Process the function (use a different callback that doesn't interfere with the loop)
                self.process_function(prompt, current_func)
                
            except Exception as e:
                print(f"Error processing function at {hex(addr)}: {str(e)}")
    
    def create_large_function_prompt(self, func_context, current_func):
        return f"""Analyze the following decompiled pseudocode from IDA Pro. 

This is a LARGE FUNCTION. Please focus on core functionality only.

Function Context:
{func_context}

Decompiled Pseudocode (IDA Pro):
{str(current_func)}

Analyze what this function actually does based on the code logic and its context. Pay close attention to:
1. What functions call this function (look at "Called by:" section)
2. What functions this function calls (look at "Calls:" section)
3. Any meaningful string or data references

The function's call graph context is essential for understanding its purpose. Look for patterns in the calling functions and called functions that could indicate its role. If caller functions are related to security, attestation, or protection, consider whether this function contributes to that functionality.

IMPORTANT: Respond ONLY with a valid JSON object that strictly follows this format:
{{
  "comment": "Brief explanation of the core functionality based on the actual code logic and its calling context",
  "function_name": "suggestedFunctionName",
  "variables": [
    {{"original_name": "v1", "new_name": "betterName"}},
    {{"original_name": "a1", "new_name": "betterName"}}
  ],
  "security_role": ""
}}

Rename as many variables as possible to make the code more readable - do not limit the number of renamed variables.
"""
    
    def create_standard_prompt(self, binary_info, func_context, current_func):
        return f"""Analyze the following pseudocode from IDA Pro.

Binary Information:
- Filename: {binary_info["filename"]}
- Architecture: {binary_info["processor"]} {binary_info["bitness"]}
- iOS Binary: {"Yes" if binary_info["is_ios"] else "Likely not"}

Function Context:
{func_context}

Decompiled Pseudocode (IDA Pro):
{str(current_func)}

Please analyze this decompiled pseudocode thoroughly, considering:
1. The function's actual code logic
2. Functions that call this function (look at "Called by:" section)
3. Functions that this function calls (look at "Calls:" section)
4. Any string references or data references

Consider the relationships between this function and its callers/callees to determine its purpose. Function names of callers and callees can provide important clues about this function's purpose.

Provide:
1. A clear explanation of what this function does based on code logic and its calling context
2. A better function name that describes its purpose based on both operations and context
3. Better variable names to improve code readability (keeping in mind IDA Pro's naming conventions like v1, a1, etc.)

IMPORTANT: Your response MUST be a valid JSON object following this format:
{{
  "comment": "Explanation of what the function does based on code analysis and context",
  "function_name": "descriptiveName",
  "variables": [
    {{"original_name": "v1", "new_name": "betterName"}},
    {{"original_name": "a1", "new_name": "betterName"}}
  ],
  "security_role": ""
}}

Fill in the security_role field ONLY if the function's relationship to security is ABSOLUTELY clear from its code or context.

DO NOT include any explanatory text outside of the JSON structure. Ensure your JSON is valid and properly formatted.
"""
    
    def process_function(self, prompt, current_func):

        print("Sending API request...")
        try:
            # Make a synchronous API call
            headers = {
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost",
            }

            data = {
                "model": OPENROUTER_MODEL,
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant specializing in code analysis, reverse engineering, and code improvement. ALWAYS provide your responses in valid JSON format as specified in the user's request."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.4,
                "max_tokens": 100000,
                "top_p": 1,
                "frequency_penalty": 1,
                "presence_penalty": 1,
                "response_format": {"type": "json_object"}
            }

            response = requests.post(
                f"{OPENROUTER_BASE_URL}/chat/completions",
                headers=headers,
                json=data,
                timeout=180
            )

            response_json = response.json()
            
            if 'error' in response_json:
                print(f"API error: {response_json['error']}")
                return
                
            content = response_json['choices'][0]['message']['content']
            
            # Process the response
            result = None
            try:
                result = json.loads(content)
                print("Successfully parsed JSON response")
            except json.JSONDecodeError:
                print("Couldn't parse response as JSON, trying extraction methods...")
                # Use existing extraction methods
                extraction_methods = [
                    lambda r: re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', r),
                    lambda r: extract_json_object(r),
                    lambda r: re.search(r'(?:Here\'s the JSON|JSON response|Response):\s*(\{[\s\S]*\})', r, re.IGNORECASE),
                    lambda r: re.search(r'(\{(?:"(?:\\.|[^"\\])*"|\[(?:\\.|[^"\\])*\]|[^{}]|(?1))*\})', r)
                ]
                
                for method_func in extraction_methods:
                    match_result = method_func(content)
                    if isinstance(match_result, re.Match) and match_result:
                        try:
                            json_str = match_result.group(1)
                            result = json.loads(json_str)
                            print(f"Successfully extracted JSON using method {extraction_methods.index(method_func) + 1}")
                            break
                        except json.JSONDecodeError:
                            continue
                    elif isinstance(match_result, dict):
                        result = match_result
                        print("Successfully extracted JSON using balanced brace matching")
                        break
                
                if result is None:
                    print("All JSON extraction methods failed. Using component extraction fallback.")
                    result = extract_components_from_text(content)
            
            if result:
                apply_changes(result, current_func)
            
        except Exception as e:
            print(f"Error in API request: {str(e)}")

    # This action is always available
    def update(self, ctx):
        return idaapi.AST_ENABLE_ALWAYS




def analyze_callback(response, current_func, view):

    print("Processing AI response...")

    # Log the raw response for debugging
    log_response = response[:200] + "..." if len(response) > 200 else response
    print(f"Raw response (truncated): {log_response}")

    result = None

    # First try to parse the entire response as JSON
    try:
        result = json.loads(response)
        print("Successfully parsed JSON response")
    except json.JSONDecodeError:
        print("Couldn't parse full response as JSON, trying extraction methods...")

        # Try different methods for extracting JSON
        extraction_methods = [
            # Method 1: Extract JSON from code blocks
            lambda r: re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', r),

            # Method 2: Find the outermost JSON object using balanced braces
            lambda r: extract_json_object(r),

            # Method 3: Look for JSON-like content after specific markers
            lambda r: re.search(r'(?:Here\'s the JSON|JSON response|Response):\s*(\{[\s\S]*\})', r, re.IGNORECASE),

            # Method 4: Try to find any JSON-like structure
            lambda r: re.search(r'(\{(?:"(?:\\.|[^"\\])*"|\[(?:\\.|[^"\\])*\]|[^{}]|(?1))*\})', r)
        ]

        for method_func in extraction_methods:
            match_result = method_func(response)
            if isinstance(match_result, re.Match) and match_result:
                try:
                    json_str = match_result.group(1)
                    result = json.loads(json_str)
                    print(f"Successfully extracted JSON using method {extraction_methods.index(method_func) + 1}")
                    break
                except json.JSONDecodeError:
                    continue
            elif isinstance(match_result, dict):
                result = match_result
                print("Successfully extracted JSON using balanced brace matching")
                break

        # If all extraction methods fail, fall back to component extraction
        if result is None:
            print("All JSON extraction methods failed. Using component extraction fallback.")
            result = extract_components_from_text(response)

    # Execute the update in the main thread
    def update_in_main_thread():
        apply_changes(result, current_func)
        return 0

    ida_kernwin.execute_sync(update_in_main_thread, ida_kernwin.MFF_WRITE)

    # Refresh the view if needed
    if view:
        view.refresh_view(True)

    print("OpenRouter query completed successfully")

def extract_json_object(text):

    start_idx = text.find('{')
    if start_idx == -1:
        return None

    # Track brace nesting
    brace_count = 0
    in_string = False
    escape_next = False

    for i in range(start_idx, len(text)):
        char = text[i]

        # Handle string literals and escaping
        if char == '\\' and not escape_next:
            escape_next = True
            continue

        if char == '"' and not escape_next:
            in_string = not in_string

        escape_next = False

        # Only count braces outside of strings
        if not in_string:
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    # Extract the JSON object and try to parse it
                    json_str = text[start_idx:i + 1]
                    try:
                        return json.loads(json_str)
                    except json.JSONDecodeError:
                        # Continue looking for valid JSON
                        pass

    return None

def extract_components_from_text(text):

    result = {
        "comment": "",
        "function_name": "",
        "variables": [],
        "security_role": ""
    }

    name_patterns = [
        r'(?:better function name|suggested name|function_name|rename the function to)[\s\n]*[:`\'"]([a-zA-Z0-9_]+)[`\'"]',
        r'function_name[\s\n]*:[\s\n]*"([a-zA-Z0-9_]+)"',
        r'I would name this function[\s\n]*["`\':]([a-zA-Z0-9_]+)[`\'"]',
        r'Better name:[\s\n]*"?([a-zA-Z0-9_]+)"?'
    ]

    for pattern in name_patterns:
        name_match = re.search(pattern, text, re.IGNORECASE)
        if name_match:
            result["function_name"] = name_match.group(1)
            print(f"Extracted function name: {result['function_name']}")
            break

    role_patterns = [
        r'(?:security role|security_role)[\s\n]*[:`\'"]([^"\']+)[`\'"]',
        r'security_role[\s\n]*:[\s\n]*"([^"]+)"',
        r'(?:This function appears to|This function is) (?:be |)(?:related to|part of|involved in) ([^.]+) security',
        r'Security implications:[\s\n]*([^.]+)'
    ]

    for pattern in role_patterns:
        role_match = re.search(pattern, text, re.IGNORECASE)
        if role_match:
            result["security_role"] = role_match.group(1).strip()
            print(f"Extracted security role: {result['security_role']}")
            break

    explanation_patterns = [
        r'(?:Function description|Function purpose|What this function does):[\s\n]*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|$)',
        r'(?:comment|explanation)[\s\n]*:[\s\n]*"([^"]+)"',
        r'(?:This function|The function)[\s\n]*([^.]+(?:\.[^.]+){0,5})'
    ]

    for pattern in explanation_patterns:
        explanation_match = re.search(pattern, text, re.IGNORECASE)
        if explanation_match:
            result["comment"] = explanation_match.group(1).strip()
            if len(result["comment"]) > 20:  # Ensure we have a meaningful comment
                print(f"Extracted comment: {result['comment'][:50]}...")
                break

    # If we still don't have a comment, use the first paragraph
    if not result["comment"]:
        paragraphs = re.split(r'\n\s*\n', text)
        if paragraphs:
            result["comment"] = paragraphs[0].strip()
            print(f"Using first paragraph as comment: {result['comment'][:50]}...")

    var_section_match = re.search(r'(?:variable|parameter)s?[\s\n]*names?:([^#]+?)(?:\n\n|$)', text, re.IGNORECASE)

    if var_section_match:
        var_section = var_section_match.group(1)
        # Find all name pairs in the section
        var_matches = re.findall(
            r'([a-zA-Z0-9_]+)[\s\n]*(?:->|→|:|should be renamed to|rename to)[\s\n]*([a-zA-Z0-9_]+)', var_section)
        for original, new in var_matches:
            if original != new and original.strip() and new.strip():
                result["variables"].append({"original_name": original.strip(), "new_name": new.strip()})
    else:
        # No dedicated section, try to find renames throughout the text
        var_matches = re.findall(
            r'([a-zA-Z0-9_]+)[\s\n]*(?:->|→|:|should be renamed to|rename to)[\s\n]*([a-zA-Z0-9_]+)', text)
        for original, new in var_matches:
            if original != new and original.strip() and new.strip():
                result["variables"].append({"original_name": original.strip(), "new_name": new.strip()})

    # Look for variable arrays in text that might be formatted like code
    var_array_match = re.search(r'variables[\s\n]*:[\s\n]*\[([\s\S]*?)\]', text, re.IGNORECASE)
    if var_array_match:
        try:
            # Try to parse as JSON array
            vars_json = "[" + var_array_match.group(1) + "]"
            # Clean up potential issues like trailing commas
            vars_json = re.sub(r',\s*]', ']', vars_json)
            vars_array = json.loads(vars_json)
            for var in vars_array:
                if "original_name" in var and "new_name" in var:
                    result["variables"].append(var)
        except json.JSONDecodeError:
            # If JSON parsing fails, try to extract manually
            var_item_matches = re.findall(r'{\s*"original_name"\s*:\s*"([^"]+)"\s*,\s*"new_name"\s*:\s*"([^"]+)"\s*}',
                                          var_array_match.group(1))
            for original, new in var_item_matches:
                result["variables"].append({"original_name": original, "new_name": new})

    print(f"Extracted {len(result['variables'])} variable renames")
    return result

def apply_changes(result, current_func):

    try:
        # Combine comment with security role if available
        comment_text = result.get("comment", "")
        if result.get("security_role"):
            comment_text = f"SECURITY ROLE: {result['security_role']}\n\n{comment_text}"

        # Set function comment if provided
        if comment_text:
            new_cmt = '\n'.join(textwrap.wrap(comment_text, width=80))
            cf = ida_funcs.get_func(current_func.entry_ea)
            if cf:
                ida_funcs.set_func_cmt(cf, new_cmt, False)
                print(f"Set function comment for {hex(current_func.entry_ea)}")

        # Rename function if a name was suggested
        if result.get("function_name"):
            new_name = f"{result['function_name']}_{hex(current_func.entry_ea)[2:]}"
            print(f"Attempting to rename function to: {new_name}")

            if ida_name.set_name(current_func.entry_ea, new_name, ida_name.SN_CHECK):
                print(f"Successfully renamed function to: {new_name}")
            else:
                print(f"Failed to rename function to: {new_name}")

        # Rename variables
        if "variables" in result:
            for var in result["variables"]:
                if "original_name" in var and "new_name" in var:
                    original_name = var["original_name"]
                    new_name = var["new_name"]
                    print(f"Attempting to rename variable: {original_name} -> {new_name}")

                    if ida_hexrays.rename_lvar(current_func.entry_ea, original_name, new_name):
                        print(f"Successfully renamed variable: {original_name} -> {new_name}")
                    else:
                        print(f"Failed to rename variable: {original_name}")

        current_func.refresh_func_ctext()
        print(f"Successfully updated function at {hex(current_func.entry_ea)}")

    except Exception as e:
        print(f"Error applying changes: {str(e)}")

def query_model(query, cb, max_tokens=100000):

    try:
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost",  # Required by OpenRouter
        }

        data = {
            "model": OPENROUTER_MODEL,
            "messages": [
                {"role": "system",
                 "content": "You are a helpful assistant specializing in code analysis, reverse engineering, and code improvement. ALWAYS provide your responses in valid JSON format as specified in the user's request."},
                {"role": "user", "content": query}
            ],
            "temperature": 0.4,  # Reduced temperature for more deterministic outputs
            "max_tokens": max_tokens,
            "top_p": 1,
            "frequency_penalty": 1,
            "presence_penalty": 1,
            "response_format": {"type": "json_object"}  # Request JSON format if supported by the model
        }

        print("Sending request to OpenRouter API...")
        response = requests.post(
            f"{OPENROUTER_BASE_URL}/chat/completions",
            headers=headers,
            json=data,
            timeout=180  # Increased timeout for large functions
        )

        response_json = response.json()

        if 'error' in response_json:
            print(f"OpenRouter error: {response_json['error']}")
            # Create a fallback result
            fallback_result = {
                "comment": f"Analysis failed with API error: {response_json.get('error', {}).get('message', 'Unknown error')}",
                "function_name": "",
                "variables": [],
                "security_role": ""
            }
            ida_kernwin.execute_sync(functools.partial(cb, response=json.dumps(fallback_result)), ida_kernwin.MFF_WRITE)
            return

        result = response_json['choices'][0]['message']['content']
        ida_kernwin.execute_sync(functools.partial(cb, response=result), ida_kernwin.MFF_WRITE)

    except requests.exceptions.RequestException as e:
        # Handle token limit errors from OpenRouter
        error_msg = str(e)
        print(f"Request exception: {error_msg}")

        if "maximum context length" in error_msg:
            m = re.search(r'maximum context length is (\d+) tokens, however you requested \d+ tokens \((\d+) in your '
                          r'prompt;', error_msg)
            if m:
                (hard_limit, prompt_tokens) = (int(m.group(1)), int(m.group(2)))
                max_tokens = hard_limit - prompt_tokens
                if max_tokens >= 100000:
                    print(f"Context length exceeded! Reducing the completion tokens to {max_tokens}...")
                    query_model(query, cb, max_tokens)
                else:
                    print("Unfortunately, this function is too big to be analyzed with the model's current API limits.")
                    # Create a fallback result for too-large functions
                    fallback_result = {
                        "comment": "This function is too large to be analyzed with the current API limits.",
                        "function_name": "large_function",
                        "variables": [],
                        "security_role": ""
                    }
                    ida_kernwin.execute_sync(functools.partial(cb, response=json.dumps(fallback_result)),
                                             ida_kernwin.MFF_WRITE)
            else:
                print(f"OpenRouter could not complete the request: {error_msg}")
                # Generic fallback for other limit errors
                fallback_result = {
                    "comment": f"Analysis failed: {error_msg}",
                    "function_name": "",
                    "variables": [],
                    "security_role": ""
                }
                ida_kernwin.execute_sync(functools.partial(cb, response=json.dumps(fallback_result)),
                                         ida_kernwin.MFF_WRITE)
        else:
            print(f"Request to OpenRouter failed: {error_msg}")
            # Generic fallback for other request errors
            fallback_result = {
                "comment": f"Analysis failed with request error: {error_msg}",
                "function_name": "",
                "variables": [],
                "security_role": ""
            }
            ida_kernwin.execute_sync(functools.partial(cb, response=json.dumps(fallback_result)), ida_kernwin.MFF_WRITE)
    except Exception as e:
        print(f"General exception encountered while running the query: {str(e)}")
        # Generic fallback for any other exception
        fallback_result = {
            "comment": f"Analysis failed with error: {str(e)}",
            "function_name": "",
            "variables": [],
            "security_role": ""
        }
        ida_kernwin.execute_sync(functools.partial(cb, response=json.dumps(fallback_result)), ida_kernwin.MFF_WRITE)


# -----------------------------------------------------------------------------

def query_model_async(query, cb):
    """
    Function which sends a query to OpenRouter and calls a callback when the response is available.
    :param query: The request to send to OpenRouter
    :param cb: The function to which the response will be passed to.
    """
    print("Request to OpenRouter sent...")
    t = threading.Thread(target=query_model, args=[query, cb])
    t.start()


# -----------------------------------------------------------------------------

def retry_with_json_formatting(response, original_prompt, cb):
    """
    Function to retry the API call with explicit instructions to format as JSON
    :param response: The original malformed response
    :param original_prompt: The original prompt
    :param cb: The callback function
    """
    retry_prompt = f"""I received the following response from you, but it's not properly formatted as valid JSON:

    {response}

    Please reformat your response as a valid JSON object using this structure:
    {{
      "comment": "Explanation of the function",
      "function_name": "suggestedName",
      "variables": [
        {{"original_name": "v1", "new_name": "betterName"}},
        {{"original_name": "a2", "new_name": "betterName"}}
      ],
      "security_role": ""
    }}

    ONLY output the JSON object with no additional text, explanation, or markdown.
    """

    print("Retrying with explicit JSON formatting instructions...")
    query_model_async(retry_prompt, cb)


# =============================================================================
# Main
# =============================================================================

def PLUGIN_ENTRY():
    print("[DEBUG] Starting VulChat plugin initialization...")
    if not OPENROUTER_API_KEY:
        globals()["OPENROUTER_API_KEY"] = os.getenv("OPENROUTER_API_KEY")
        if not OPENROUTER_API_KEY:
            print("Please edit this script to insert your OpenRouter API key!")
            raise ValueError("No valid OpenRouter API key found")
    
    plugin = VulChatPlugin()
    print("[DEBUG] VulChat plugin initialized successfully")
    return plugin