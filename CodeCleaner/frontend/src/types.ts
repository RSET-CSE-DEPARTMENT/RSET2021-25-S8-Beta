export type Theme = 'dark' | 'light';

export interface EditorProps {
  code: string;
  onChange: (value: string) => void;
  language?: string;
  theme: Theme;
}

export interface TerminalProps {
  messages: string[];
  theme: Theme;
}