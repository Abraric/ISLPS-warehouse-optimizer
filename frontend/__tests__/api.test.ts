/**
 * Frontend API client tests
 */
import { healthCheck } from '@/lib/api'

describe('API Client', () => {
  it('should have health check function', () => {
    expect(typeof healthCheck).toBe('function')
  })
})

