import { create } from "zustand";

interface AppState {
  selectedSymbol: string;
  selectedTimeframe: string;
  sidebarCollapsed: boolean;
  setSelectedSymbol: (symbol: string) => void;
  setSelectedTimeframe: (tf: string) => void;
  toggleSidebar: () => void;
}

export const useAppStore = create<AppState>((set) => ({
  selectedSymbol: "BTC",
  selectedTimeframe: "1h",
  sidebarCollapsed: false,
  setSelectedSymbol: (symbol) => set({ selectedSymbol: symbol }),
  setSelectedTimeframe: (tf) => set({ selectedTimeframe: tf }),
  toggleSidebar: () =>
    set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed })),
}));
