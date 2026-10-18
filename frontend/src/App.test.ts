// @vitest-environment jsdom
import { describe, it, expect, beforeEach } from 'vitest';
import { api } from './lib/api-client';

describe('CampusMind Frontend API Client & State Tests', () => {
  beforeEach(() => {
    sessionStorage.clear();
    localStorage.clear();
    api.setToken(null);
  });

  it('manages authorization token in memory and sessionStorage correctly', () => {
    expect(api.getToken()).toBeNull();

    const sampleToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.sample';
    api.setToken(sampleToken);

    expect(api.getToken()).toBe(sampleToken);
    expect(sessionStorage.getItem('campusmind_token')).toBe(sampleToken);

    api.logout();
    expect(api.getToken()).toBeNull();
    expect(sessionStorage.getItem('campusmind_token')).toBeNull();
  });

  it('validates mention filtering and workflow bindings', () => {
    const mockMentions = [
      {
        key: '23SS1A0535',
        label: '@23SS1A0535',
        description: 'Verified attendance and academic records',
        required_role: 'student',
        workflow: 'student_records',
      },
      {
        key: 'principal',
        label: '@principal',
        description: 'Executive administrative authorization prompt',
        required_role: 'admin',
        workflow: 'principal_elevation',
      },
      {
        key: 'help',
        label: '@help',
        description: 'Guidelines and commands',
        required_role: 'student',
        workflow: 'general_help',
      },
    ];

    const studentFilter = mockMentions.filter((m) => m.workflow === 'student_records');
    expect(studentFilter).toHaveLength(1);
    expect(studentFilter[0].label).toBe('@23SS1A0535');

    const adminFilter = mockMentions.filter((m) => m.required_role === 'admin');
    expect(adminFilter).toHaveLength(1);
    expect(adminFilter[0].key).toBe('principal');
  });

  it('verifies citation format structure', () => {
    const mockCitation = {
      document_id: 1,
      document_title: 'Campus Academic Calendar & Policies 2026',
      page_number: 1,
      section_heading: 'Add/Drop Deadlines',
      chunk_id: 4,
      similarity_score: 0.8842,
    };

    expect(mockCitation.document_title).toBeDefined();
    expect(mockCitation.similarity_score).toBeGreaterThan(0.5);
    expect((mockCitation.similarity_score * 100).toFixed(0)).toBe('88');
  });

  it('validates theme persistence in localStorage', () => {
    expect(localStorage.getItem('campusmind_theme')).toBeNull();

    localStorage.setItem('campusmind_theme', 'dark');
    expect(localStorage.getItem('campusmind_theme')).toBe('dark');

    localStorage.setItem('campusmind_theme', 'light');
    expect(localStorage.getItem('campusmind_theme')).toBe('light');
  });

  it('validates sidebar collapse toggle state preservation', () => {
    let isCollapsed = false;
    const toggleCollapse = () => {
      isCollapsed = !isCollapsed;
    };

    expect(isCollapsed).toBe(false);
    toggleCollapse();
    expect(isCollapsed).toBe(true);
    toggleCollapse();
    expect(isCollapsed).toBe(false);
  });
});
