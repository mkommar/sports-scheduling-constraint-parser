"use client"

import { useState } from "react"
import { useAuth } from "@/lib/auth-context"
import { LoginForm } from "./login-form"
import { SignupForm } from "./signup-form"
import { Loader2, Sparkles } from "lucide-react"

export function AuthGate({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth()
  const [mode, setMode] = useState<"login" | "signup">("login")

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-b from-background to-muted/20">
        <div className="text-center space-y-4">
          <Loader2 className="h-12 w-12 animate-spin mx-auto text-primary" />
          <p className="text-muted-foreground">Loading...</p>
        </div>
      </div>
    )
  }

  if (!user) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-b from-background to-muted/20 p-4">
        <div className="text-center space-y-4 mb-8">
          <div className="flex items-center justify-center space-x-2">
            <Sparkles className="h-8 w-8 text-primary" />
            <h1 className="text-3xl md:text-4xl font-bold">Sports Constraint Parser</h1>
          </div>
          <p className="text-muted-foreground max-w-md">
            AI-powered natural language to scheduling constraints
          </p>
        </div>
        
        {mode === "login" ? (
          <LoginForm onToggleMode={() => setMode("signup")} />
        ) : (
          <SignupForm onToggleMode={() => setMode("login")} />
        )}
      </div>
    )
  }

  return <>{children}</>
}

