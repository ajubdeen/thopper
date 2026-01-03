import { ReactNode } from "react";
import { cn } from "@/lib/utils";

interface SteampunkButtonProps {
  children: ReactNode;
  onClick?: () => void;
  disabled?: boolean;
  variant?: "primary" | "secondary" | "ghost";
  size?: "sm" | "md" | "lg";
  className?: string;
  "data-testid"?: string;
}

export function SteampunkButton({
  children,
  onClick,
  disabled = false,
  variant = "primary",
  size = "md",
  className,
  "data-testid": testId
}: SteampunkButtonProps) {
  const sizeStyles = {
    sm: "px-4 py-2 text-sm",
    md: "px-8 py-4 text-lg",
    lg: "px-12 py-5 text-xl"
  };

  const variantStyles = {
    primary: "steampunk-button-primary",
    secondary: "steampunk-button-secondary", 
    ghost: "steampunk-button-ghost"
  };

  return (
    <button
      onClick={onClick}
      disabled={disabled}
      data-testid={testId}
      className={cn(
        "steampunk-button",
        variantStyles[variant],
        sizeStyles[size],
        disabled && "opacity-50 cursor-not-allowed",
        className
      )}
    >
      {/* Inner glow effect */}
      <span className="steampunk-button-glow" />
      
      {/* Button content */}
      <span className="steampunk-button-text relative z-10">
        {children}
      </span>
      
      {/* Corner decorations */}
      <span className="steampunk-corner steampunk-corner-tl" />
      <span className="steampunk-corner steampunk-corner-tr" />
      <span className="steampunk-corner steampunk-corner-bl" />
      <span className="steampunk-corner steampunk-corner-br" />
    </button>
  );
}

export default SteampunkButton;
