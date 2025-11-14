"use client"

import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import { Activity } from "lucide-react"

export function Navbar() {
  return (
    <nav className="border-b bg-background">
      <div className="container mx-auto px-4 h-16 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <Activity className="h-6 w-6 text-primary" />
          <span className="text-xl font-bold">Sports Constraint Parser</span>
        </div>
        
        <div className="flex items-center space-x-4">
          <Button variant="ghost" size="sm">
            Templates
          </Button>
          <Button variant="ghost" size="sm">
            Docs
          </Button>
          <Avatar className="h-9 w-9">
            <AvatarFallback>U</AvatarFallback>
          </Avatar>
        </div>
      </div>
    </nav>
  )
}

