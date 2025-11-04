// >>> PAPSAS v1.3 BEGIN
import { describe, it, expect } from 'vitest';
import { toCsv } from '../../lib/csv';

describe('toCsv', () => {
  it('serializes rows to CSV with headers', () => {
    const csv = toCsv([
      { a: 1, b: 'x' },
      { a: 2, b: 'y,z' },
    ]);
    expect(csv.split('\n')[0]).toBe('a,b');
    expect(csv).toContain('1,x');
    expect(csv).toContain('2,"y,z"');
  });
});
// <<< PAPSAS v1.3 END

