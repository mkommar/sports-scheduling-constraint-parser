# Testing Guide

## Overview

This guide covers manual testing procedures for the Sports Scheduling Constraint Parser application.

## Prerequisites

- Application running locally (`npm run dev`)
- Database seeded with examples (`curl -X POST http://localhost:3000/api/seed`)
- Environment variables configured

## Test Cases

### 1. Template 1: Game Scheduling

#### Test 1.1: Basic Game Scheduling
**Input**: "Ensure all rivalry games are scheduled on weekends and broadcast on ESPN"

**Expected Output**:
- Template ID: 1
- Template Name: "Game Scheduling"
- Confidence: > 80%
- Parameters should include:
  - teams: "rivalry_games"
  - rounds: "weekend" or "weekend_rounds"
  - networks: "ESPN"
- Feasibility: Feasible
- No warnings

#### Test 1.2: Negation Handling
**Input**: "Don't schedule rivalry games on weekdays"

**Expected Output**:
- Template ID: 1
- Parameters should include:
  - max: 0 (indicating negation)
- Feasibility may show warnings about negation

#### Test 1.3: Multiple Networks
**Input**: "Schedule playoff games on ESPN or FOX during primetime"

**Expected Output**:
- Template ID: 1
- Parameters should include:
  - teams: "playoff" or "playoff_games"
  - networks: "ESPN" or "FOX" (may vary)
  - time_slots or rounds: "primetime"

### 2. Template 2: Time Slot Constraints

#### Test 2.1: Maximum Games Per Slot
**Input**: "Limit ESPN to maximum 2 games in primetime slots"

**Expected Output**:
- Template ID: 2
- Template Name: "Time Slot Constraints"
- Confidence: > 75%
- Parameters should include:
  - max: 2
  - networks: "ESPN"
  - time_slots: "primetime"
- Feasibility: Feasible

#### Test 2.2: Minimum Games Requirement
**Input**: "Ensure FOX broadcasts at least 1 game during afternoon slots"

**Expected Output**:
- Template ID: 2
- Parameters should include:
  - min: 1
  - networks: "FOX"
  - time_slots: "afternoon"
- Feasibility: Feasible

#### Test 2.3: High Capacity Warning
**Input**: "Schedule 15 games on CBS in primetime"

**Expected Output**:
- Template ID: 2
- Parameters should include:
  - min or max: 15
- Feasibility: May show warning about high game count
- Suggestions about distributing games

### 3. Template 3: Team-specific Constraints

#### Test 3.1: Rest Days
**Input**: "Ensure Lakers have at least 2 rest days between back-to-back games"

**Expected Output**:
- Template ID: 3
- Template Name: "Team-specific Constraints"
- Confidence: > 70%
- Parameters should include:
  - teams: "Lakers"
  - min: 2
  - condition: "rest" or "back-to-back"
- Feasibility: Feasible

#### Test 3.2: Consecutive Games
**Input**: "Limit Warriors to maximum 3 consecutive home games"

**Expected Output**:
- Template ID: 3
- Parameters should include:
  - teams: "Warriors"
  - max: 3
  - condition: "consecutive" or "home"
- Feasibility: Feasible

#### Test 3.3: Weekly Constraints
**Input**: "Celtics should have between 1 and 2 primetime games per week"

**Expected Output**:
- Template ID: 3
- Parameters should include:
  - teams: "Celtics"
  - min: 1
  - max: 2
  - condition: "primetime" or "weekly"
- Feasibility: Feasible

### 4. Edge Cases

#### Test 4.1: Empty Query
**Input**: ""

**Expected Output**:
- Error: "Query is required and must be a string"
- Status: 400

#### Test 4.2: Very Long Query
**Input**: "I need to ensure that all of the rivalry games including but not limited to the Lakers versus Celtics and Warriors versus Cavaliers are scheduled on weekend time slots specifically Saturday and Sunday during primetime hours and broadcast exclusively on major networks like ESPN or FOX with proper venue allocation"

**Expected Output**:
- Should still parse successfully
- May have lower confidence
- Should extract key parameters

#### Test 4.3: Ambiguous Query
**Input**: "Schedule some games"

**Expected Output**:
- Should match to Template 1 (likely)
- Lower confidence (< 70%)
- Generic parameters
- May show feasibility warnings about being too broad

#### Test 4.4: Conflicting Constraints
**Input**: "Ensure minimum 10 and maximum 5 games on ESPN"

**Expected Output**:
- Should parse successfully
- Parameters: min: 10, max: 5
- Feasibility: NOT feasible
- Warning: "Minimum value (10) is greater than maximum value (5)"
- Suggestion to adjust values

### 5. UI/UX Tests

#### Test 5.1: Loading State
**Action**: Submit a query

**Expected Behavior**:
- Input becomes disabled
- Button shows "Parsing..." with spinner
- Previous results remain visible until new results load

#### Test 5.2: Example Queries
**Action**: Click any example query button

**Expected Behavior**:
- Query automatically submits
- Results display correctly
- Can click another example immediately after

#### Test 5.3: Accordion Expansion
**Action**: Click "Expand Parameters"

**Expected Behavior**:
- Accordion opens smoothly
- Parameters displayed in grid
- All parameter values visible
- Can collapse again

#### Test 5.4: Responsive Design
**Action**: Resize browser window to mobile size

**Expected Behavior**:
- Layout adapts to mobile view
- Search bar remains usable
- Cards stack vertically
- Text remains readable
- No horizontal scroll

### 6. Performance Tests

#### Test 6.1: Response Time
**Action**: Submit a query and measure time

**Expected Behavior**:
- Total time: < 2 seconds (after warm start)
- First load (cold start): < 5 seconds acceptable
- Subsequent queries: < 1.5 seconds

#### Test 6.2: Concurrent Requests
**Action**: Open multiple browser tabs, submit queries simultaneously

**Expected Behavior**:
- All requests complete successfully
- No race conditions
- No errors in console

### 7. API Testing

#### Test 7.1: Parse API - Valid Request
```bash
curl -X POST http://localhost:3000/api/parse \
  -H "Content-Type: application/json" \
  -d '{"query": "Schedule rivalry games on ESPN"}'
```

**Expected**: 200 status, valid ParseResult JSON

#### Test 7.2: Parse API - Invalid Request
```bash
curl -X POST http://localhost:3000/api/parse \
  -H "Content-Type: application/json" \
  -d '{"invalid": "field"}'
```

**Expected**: 400 status, error message

#### Test 7.3: Seed API
```bash
curl -X POST http://localhost:3000/api/seed
```

**Expected**: 200 status, success message with count

### 8. Error Handling Tests

#### Test 8.1: OpenAI API Error (Simulated)
**Setup**: Temporarily use invalid OpenAI API key

**Expected Behavior**:
- Error message displayed to user
- No app crash
- Can still navigate UI

#### Test 8.2: Supabase Connection Error (Simulated)
**Setup**: Temporarily use invalid Supabase URL

**Expected Behavior**:
- Fallback mechanism activates (if implemented)
- Error message displayed
- Graceful degradation

## Automated Testing (Future)

### Unit Tests
```typescript
// Example unit test structure
describe('generateConstraintSentence', () => {
  it('should generate correct sentence for Template 1', () => {
    // Test implementation
  })
})
```

### Integration Tests
```typescript
// Example integration test
describe('/api/parse', () => {
  it('should parse game scheduling query', async () => {
    // Test implementation
  })
})
```

### E2E Tests
```typescript
// Example E2E test with Playwright
test('user can submit query and see results', async ({ page }) => {
  // Test implementation
})
```

## Performance Benchmarks

Track these metrics:
- **P50 latency**: < 1s
- **P95 latency**: < 2s
- **P99 latency**: < 3s
- **Error rate**: < 0.1%
- **Uptime**: > 99.9%

## Accessibility Testing

### Checklist
- [ ] Keyboard navigation works
- [ ] Screen reader compatible
- [ ] Color contrast meets WCAG AA
- [ ] Focus indicators visible
- [ ] Alt text on all images
- [ ] ARIA labels on interactive elements

## Browser Compatibility

Test on:
- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Edge (latest)
- [ ] Mobile Safari (iOS)
- [ ] Chrome Mobile (Android)

## Regression Testing

Before each deployment, run:
1. All 3 template test cases
2. At least 2 edge cases
3. UI/UX responsive test
4. API endpoint tests
5. Performance baseline check

## Reporting Issues

When reporting bugs, include:
1. Input query used
2. Expected behavior
3. Actual behavior
4. Screenshots/recordings
5. Browser/device information
6. Console errors (if any)

## Test Data Cleanup

After testing:
- No need to clean up (read-only operations)
- Database can be reseeded anytime with `/api/seed`

## Next Steps

1. Implement automated test suite (Jest + React Testing Library)
2. Add E2E tests (Playwright or Cypress)
3. Set up CI/CD pipeline with test automation
4. Add performance monitoring (Vercel Analytics)
5. Implement error tracking (Sentry or similar)

