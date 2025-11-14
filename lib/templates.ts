export interface ConstraintTemplate {
  id: number
  name: string
  description: string
  template: string
  exampleQueries: string[]
}

export const constraintTemplates: ConstraintTemplate[] = [
  {
    id: 1,
    name: "Game Scheduling",
    description: "Ensures a specific number of games from a team group are scheduled in certain rounds, venues, and networks",
    template: "Ensure that at least {min} and at most {max} games from {teams} are scheduled across {rounds} and played in any venue from {venues} and assigned to {networks}.",
    exampleQueries: [
      "Ensure all rivalry games are scheduled on weekends and broadcast on ESPN",
      "Make sure at least 3 conference games are played in outdoor stadiums during primetime",
      "Schedule division games on FOX during weekend rounds",
      "Assign all playoff games to primetime slots on major networks",
      "Don't schedule rivalry games on weekdays"
    ]
  },
  {
    id: 2,
    name: "Time Slot Constraints",
    description: "Limits the number of games that can be scheduled in specific time slots for a network",
    template: "Ensure that at least {min} and at most {max} games are scheduled in {time_slots} for {networks}.",
    exampleQueries: [
      "Limit ESPN to maximum 2 games in primetime slots",
      "Ensure FOX broadcasts at least 1 game during afternoon slots",
      "Don't schedule more than 3 games on CBS in evening time slots",
      "ABC should have between 1 and 4 games in weekend primetime",
      "No more than 2 concurrent games on NBC during primetime"
    ]
  },
  {
    id: 3,
    name: "Team-specific Constraints",
    description: "Applies constraints to specific teams regarding their schedule patterns",
    template: "Ensure that {teams} have at least {min} and at most {max} {condition}.",
    exampleQueries: [
      "Ensure Lakers have at least 2 rest days between back-to-back games",
      "Limit Warriors to maximum 3 consecutive home games",
      "Celtics should have between 1 and 2 primetime games per week",
      "Don't schedule Knicks for more than 2 consecutive away games",
      "Ensure Heat have at least 1 home game every week"
    ]
  }
]

export function generateConstraintSentence(
  templateId: number,
  params: Record<string, any>
): string {
  const template = constraintTemplates.find(t => t.id === templateId)
  if (!template) return "Unknown template"

  let sentence = template.template

  // Replace placeholders with actual values or defaults
  const replacements: Record<string, string> = {
    min: params.min?.toString() || '1',
    max: params.max?.toString() || '999',
    teams: params.teams || 'all_teams',
    rounds: params.rounds || 'all_rounds',
    networks: params.networks || 'all_networks',
    venues: params.venues || 'all_venues',
    time_slots: params.time_slots || 'all_time_slots',
    condition: params.condition || 'constraints'
  }

  for (const [key, value] of Object.entries(replacements)) {
    sentence = sentence.replace(`{${key}}`, value)
  }

  return sentence
}

