"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { usePrice } from "@/lib/hooks/useMarketData";

interface Holding {
  symbol: string;
  amount: number;
  avg_buy_price: number;
}

function HoldingRow({
  holding,
  onDelete,
  onUpdate,
  isDeleting,
  isUpdating,
}: {
  holding: Holding;
  onDelete: () => void;
  onUpdate: (data: Holding) => void;
  isDeleting: boolean;
  isUpdating: boolean;
}) {
  const [editing, setEditing] = useState(false);
  const [editAmount, setEditAmount] = useState(String(holding.amount));
  const [editPrice, setEditPrice] = useState(String(holding.avg_buy_price));

  const { data: price } = usePrice(holding.symbol);
  const currentPrice = price?.price || 0;
  const currentValue = holding.amount * currentPrice;
  const costBasis = holding.amount * holding.avg_buy_price;
  const pnl = currentValue - costBasis;
  const pnlPct = costBasis > 0 ? (pnl / costBasis) * 100 : 0;
  const pnlColor = pnl >= 0 ? "text-buy" : "text-sell";

  const handleSave = () => {
    onUpdate({
      symbol: holding.symbol,
      amount: parseFloat(editAmount),
      avg_buy_price: parseFloat(editPrice),
    });
    setEditing(false);
  };

  if (editing) {
    return (
      <tr className="border-b border-border bg-background/50">
        <td className="py-3 px-4 font-medium">{holding.symbol}</td>
        <td className="py-3 px-4 text-right">
          <input
            value={editAmount}
            onChange={(e) => setEditAmount(e.target.value)}
            type="number"
            step="any"
            className="bg-background border border-accent rounded px-2 py-1 text-sm w-28 text-right"
          />
        </td>
        <td className="py-3 px-4 text-right">
          <input
            value={editPrice}
            onChange={(e) => setEditPrice(e.target.value)}
            type="number"
            step="any"
            className="bg-background border border-accent rounded px-2 py-1 text-sm w-28 text-right"
          />
        </td>
        <td colSpan={3} />
        <td className="py-3 px-4 text-right">
          <div className="flex gap-2 justify-end">
            <button
              onClick={handleSave}
              disabled={isUpdating}
              className="px-3 py-1 rounded bg-buy text-background text-xs font-medium"
            >
              Save
            </button>
            <button
              onClick={() => setEditing(false)}
              className="px-3 py-1 rounded bg-border text-foreground text-xs font-medium"
            >
              Cancel
            </button>
          </div>
        </td>
      </tr>
    );
  }

  return (
    <tr className="border-b border-border hover:bg-background/50">
      <td className="py-3 px-4 font-medium">{holding.symbol}</td>
      <td className="py-3 px-4 text-right">{holding.amount}</td>
      <td className="py-3 px-4 text-right">${holding.avg_buy_price}</td>
      <td className="py-3 px-4 text-right">
        ${currentPrice > 0 ? currentPrice.toFixed(currentPrice >= 1 ? 2 : 6) : "..."}
      </td>
      <td className="py-3 px-4 text-right">${currentValue.toFixed(2)}</td>
      <td className={`py-3 px-4 text-right font-medium ${pnlColor}`}>
        {pnl >= 0 ? "+" : ""}${pnl.toFixed(2)} ({pnlPct >= 0 ? "+" : ""}
        {pnlPct.toFixed(2)}%)
      </td>
      <td className="py-3 px-4 text-right">
        <div className="flex gap-2 justify-end">
          <button
            onClick={() => {
              setEditAmount(String(holding.amount));
              setEditPrice(String(holding.avg_buy_price));
              setEditing(true);
            }}
            className="px-3 py-1 rounded bg-accent/15 text-accent text-xs font-medium hover:bg-accent/25"
          >
            Edit
          </button>
          <button
            onClick={onDelete}
            disabled={isDeleting}
            className="px-3 py-1 rounded bg-sell/15 text-sell text-xs font-medium hover:bg-sell/25 disabled:opacity-50"
          >
            Delete
          </button>
        </div>
      </td>
    </tr>
  );
}

export default function PortfolioPage() {
  const queryClient = useQueryClient();
  const { data: holdings = [] } = useQuery<Holding[]>({
    queryKey: ["portfolio"],
    queryFn: () => api.get("/api/portfolio"),
  });

  const addMutation = useMutation({
    mutationFn: (data: Holding) => api.post<Holding>("/api/portfolio", data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["portfolio"] }),
  });

  const deleteMutation = useMutation({
    mutationFn: (symbol: string) =>
      fetch(`/api/proxy/api/portfolio/${symbol}`, { method: "DELETE" }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["portfolio"] }),
  });

  const [newSymbol, setNewSymbol] = useState("");
  const [newAmount, setNewAmount] = useState("");
  const [newPrice, setNewPrice] = useState("");

  const handleAdd = () => {
    if (!newSymbol || !newAmount || !newPrice) return;
    addMutation.mutate(
      {
        symbol: newSymbol.toUpperCase(),
        amount: parseFloat(newAmount),
        avg_buy_price: parseFloat(newPrice),
      },
      {
        onSuccess: () => {
          setNewSymbol("");
          setNewAmount("");
          setNewPrice("");
        },
      }
    );
  };

  const totalCost = holdings.reduce(
    (sum, h) => sum + h.amount * h.avg_buy_price,
    0
  );

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Portfolio</h2>

      {/* Summary */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-card border border-border rounded-xl p-5">
          <div className="text-xs text-muted">Holdings</div>
          <div className="text-2xl font-bold">{holdings.length}</div>
        </div>
        <div className="bg-card border border-border rounded-xl p-5">
          <div className="text-xs text-muted">Cost Basis</div>
          <div className="text-2xl font-bold">${totalCost.toFixed(2)}</div>
        </div>
        <div className="bg-card border border-border rounded-xl p-5">
          <div className="text-xs text-muted">Status</div>
          <div className="text-2xl font-bold text-buy">Tracking</div>
        </div>
      </div>

      {/* Holdings Table */}
      <div className="bg-card border border-border rounded-xl overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-border text-muted">
              <th className="py-3 px-4 text-left font-medium">Symbol</th>
              <th className="py-3 px-4 text-right font-medium">Amount</th>
              <th className="py-3 px-4 text-right font-medium">Avg Buy</th>
              <th className="py-3 px-4 text-right font-medium">Current</th>
              <th className="py-3 px-4 text-right font-medium">Value</th>
              <th className="py-3 px-4 text-right font-medium">P&L</th>
              <th className="py-3 px-4 text-right font-medium w-40">Actions</th>
            </tr>
          </thead>
          <tbody>
            {holdings.map((h) => (
              <HoldingRow
                key={h.symbol}
                holding={h}
                onDelete={() => deleteMutation.mutate(h.symbol)}
                onUpdate={(data) => addMutation.mutate(data)}
                isDeleting={deleteMutation.isPending}
                isUpdating={addMutation.isPending}
              />
            ))}
            {holdings.length === 0 && (
              <tr>
                <td colSpan={7} className="py-8 text-center text-muted">
                  No holdings yet. Add your first position below.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Add Holding */}
      <div className="bg-card border border-border rounded-xl p-5">
        <h3 className="text-sm font-semibold mb-3">Add Holding</h3>
        <div className="flex gap-3 items-end flex-wrap">
          <div>
            <label className="block text-xs text-muted mb-1">Symbol</label>
            <input
              value={newSymbol}
              onChange={(e) => setNewSymbol(e.target.value)}
              placeholder="BTC"
              className="bg-background border border-border rounded-lg px-3 py-2 text-sm w-24"
            />
          </div>
          <div>
            <label className="block text-xs text-muted mb-1">Amount</label>
            <input
              value={newAmount}
              onChange={(e) => setNewAmount(e.target.value)}
              placeholder="0.5"
              type="number"
              step="any"
              className="bg-background border border-border rounded-lg px-3 py-2 text-sm w-32"
            />
          </div>
          <div>
            <label className="block text-xs text-muted mb-1">
              Avg Buy Price ($)
            </label>
            <input
              value={newPrice}
              onChange={(e) => setNewPrice(e.target.value)}
              placeholder="0.057"
              type="number"
              step="any"
              className="bg-background border border-border rounded-lg px-3 py-2 text-sm w-32"
            />
          </div>
          <button
            onClick={handleAdd}
            disabled={addMutation.isPending || !newSymbol || !newAmount || !newPrice}
            className="bg-accent text-background px-4 py-2 rounded-lg text-sm font-medium hover:bg-accent/90 disabled:opacity-50"
          >
            {addMutation.isPending ? "Adding..." : "Add"}
          </button>
        </div>
      </div>
    </div>
  );
}
