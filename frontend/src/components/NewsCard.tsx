import { cn } from "@/lib/utils";
import { ExternalLink } from "lucide-react";

interface NewsCardProps {
    headline: string;
    source?: string;
    link?: string;
    stance: string;
    confidence: number;
    className?: string;
}

export function NewsCard({ headline, source, link, stance, confidence, className }: NewsCardProps) {
    const stanceColor = {
        positive: "bg-emerald-100 text-emerald-800 border-emerald-200",
        negative: "bg-rose-100 text-rose-800 border-rose-200",
        neutral: "bg-gray-100 text-gray-800 border-gray-200",
    }[stance] || "bg-gray-100 text-gray-800";

    return (
        <div className={cn("p-4 rounded-lg border bg-white shadow-sm hover:shadow-md transition-shadow", className)}>
            <div className="flex justify-between items-start gap-2">
                <span className={cn("text-xs font-medium px-2 py-0.5 rounded-full border capitalize", stanceColor)}>
                    {stance} ({Math.round(confidence * 100)}%)
                </span>
                {link && (
                    <a href={link} target="_blank" rel="noopener noreferrer" className="text-gray-400 hover:text-gray-600">
                        <ExternalLink className="h-4 w-4" />
                    </a>
                )}
            </div>
            <h3 className="mt-2 font-medium text-gray-900 leading-tight">
                {link ? (
                    <a href={link} target="_blank" rel="noopener noreferrer" className="hover:underline">
                        {headline}
                    </a>
                ) : (
                    headline
                )}
            </h3>
            {source && <p className="mt-2 text-xs text-gray-500">{source}</p>}
        </div>
    );
}
