"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";

interface UserSettings {
  symbols: string[];
  email: string;
  alert_preferences: Record<string, boolean>;
}

export function useSettings() {
  return useQuery<UserSettings>({
    queryKey: ["settings"],
    queryFn: () => api.get("/api/settings"),
  });
}

export function useUpdateSettings() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (update: Partial<UserSettings>) =>
      api.put("/api/settings", update),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["settings"] });
    },
  });
}
