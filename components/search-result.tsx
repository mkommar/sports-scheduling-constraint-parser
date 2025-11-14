"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion"
import { Badge } from "@/components/ui/badge"
import { CheckCircle2, AlertTriangle, Info } from "lucide-react"

interface ParseResult {
  templateId: number
  templateName: string
  confidence: number
  constraintSentence: string
  parameters: Record<string, any>
  feasibility: {
    feasible: boolean
    confidence: number
    warnings: string[]
    suggestions: string[]
  }
  matchReason: string
  originalQuery?: string
}

interface SearchResultProps {
  result: ParseResult
}

export function SearchResult({ result }: SearchResultProps) {
  const confidencePercent = Math.round(result.confidence * 100)
  const feasibilityPercent = Math.round(result.feasibility.confidence * 100)

  return (
    <div className="w-full max-w-4xl mx-auto space-y-4 animate-in fade-in slide-in-from-bottom-4 duration-500">
      {/* Template Match Card */}
      <Card>
        <CardHeader>
          <div className="flex items-start justify-between">
            <div className="space-y-1">
              <div className="flex items-center space-x-2">
                <CheckCircle2 className="h-5 w-5 text-green-600" />
                <CardTitle>Template {result.templateId}: {result.templateName}</CardTitle>
              </div>
              <CardDescription>
                Confidence: <span className="font-semibold text-foreground">{confidencePercent}%</span>
              </CardDescription>
            </div>
            <Badge variant={confidencePercent >= 80 ? "default" : "secondary"}>
              {confidencePercent >= 80 ? "High Confidence" : "Medium Confidence"}
            </Badge>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <h4 className="text-sm font-medium mb-2">Parsed Constraint:</h4>
            <p className="text-base leading-relaxed p-4 bg-muted rounded-lg">
              {result.constraintSentence}
            </p>
          </div>

          <Accordion type="single" collapsible className="w-full">
            <AccordionItem value="parameters">
              <AccordionTrigger>Expand Parameters</AccordionTrigger>
              <AccordionContent>
                <div className="grid grid-cols-2 gap-3 p-2">
                  {Object.entries(result.parameters).map(([key, value]) => (
                    <div key={key} className="flex flex-col space-y-1">
                      <span className="text-xs font-medium text-muted-foreground uppercase">
                        {key}
                      </span>
                      <span className="text-sm font-mono bg-muted px-2 py-1 rounded">
                        {value !== null && value !== undefined ? String(value) : 'null'}
                      </span>
                    </div>
                  ))}
                </div>
              </AccordionContent>
            </AccordionItem>
          </Accordion>
        </CardContent>
      </Card>

      {/* Explanation Card */}
      <Card>
        <CardHeader>
          <div className="flex items-center space-x-2">
            <Info className="h-5 w-5 text-blue-600" />
            <CardTitle className="text-lg">Why This Matched</CardTitle>
          </div>
        </CardHeader>
        <CardContent>
          <ul className="space-y-2">
            <li className="flex items-start space-x-2">
              <span className="text-muted-foreground">•</span>
              <span>{result.matchReason}</span>
            </li>
            {result.originalQuery && (
              <li className="flex items-start space-x-2">
                <span className="text-muted-foreground">•</span>
                <span>Closest example: &ldquo;{result.originalQuery}&rdquo;</span>
              </li>
            )}
            <li className="flex items-start space-x-2">
              <span className="text-muted-foreground">•</span>
              <span>Template type: {result.templateName}</span>
            </li>
          </ul>
        </CardContent>
      </Card>

      {/* Feasibility Check Card */}
      <Card className={
        result.feasibility.feasible 
          ? "border-green-200 dark:border-green-900" 
          : "border-yellow-200 dark:border-yellow-900"
      }>
        <CardHeader>
          <div className="flex items-start justify-between">
            <div className="flex items-center space-x-2">
              {result.feasibility.feasible ? (
                <CheckCircle2 className="h-5 w-5 text-green-600" />
              ) : (
                <AlertTriangle className="h-5 w-5 text-yellow-600" />
              )}
              <CardTitle className="text-lg">Feasibility Check</CardTitle>
            </div>
            <Badge variant={result.feasibility.feasible ? "default" : "secondary"}>
              {feasibilityPercent}% Confidence
            </Badge>
          </div>
        </CardHeader>
        <CardContent className="space-y-3">
          {result.feasibility.warnings.length > 0 && (
            <div>
              <h4 className="text-sm font-medium mb-2 text-yellow-700 dark:text-yellow-400">
                Warnings:
              </h4>
              <ul className="space-y-1">
                {result.feasibility.warnings.map((warning, idx) => (
                  <li key={idx} className="text-sm flex items-start space-x-2">
                    <AlertTriangle className="h-4 w-4 text-yellow-600 mt-0.5 flex-shrink-0" />
                    <span>{warning}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
          
          <div>
            <h4 className="text-sm font-medium mb-2">
              {result.feasibility.feasible ? "Analysis:" : "Suggestions:"}
            </h4>
            <ul className="space-y-1">
              {result.feasibility.suggestions.map((suggestion, idx) => (
                <li key={idx} className="text-sm flex items-start space-x-2">
                  <span className="text-muted-foreground">•</span>
                  <span>{suggestion}</span>
                </li>
              ))}
            </ul>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

