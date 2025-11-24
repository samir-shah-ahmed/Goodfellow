import { cn } from "@/lib/utils";
import { ShieldCheck, ShieldAlert, Shield } from "lucide-react";

interface SafetyBadgeProps {
    score: number; // 0.0 to 1.0
    className?: string;
}

export function SafetyBadge({ score, className }: SafetyBadgeProps) {
    let color = "bg-gray-100 text-gray-800";
    let label = "Unknown";
    let Icon = Shield;

    if (score >= 0.7) {
        color = "bg-emerald-100 text-emerald-800 border-emerald-200";
        label = "Safe";
        Icon = ShieldCheck;
    } else if (score >= 0.4) {
        color = "bg-yellow-100 text-yellow-800 border-yellow-200";
        label = "Caution";
        Icon = Shield;
    } else {
        color = "bg-rose-100 text-rose-800 border-rose-200";
        label = "Risky";
        Icon = ShieldAlert;
    }

    return (
        <div className={cn("flex items-center gap-1.5 px-3 py-1 rounded-full border", color, className)}>
            <Icon className="h-4 w-4" />
            <span className="font-semibold text-sm">{label} ({Math.round(score * 100)})</span>
        </div>
    );
}
