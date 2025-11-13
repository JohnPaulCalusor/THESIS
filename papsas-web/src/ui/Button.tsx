// src/ui/Button.tsx
export const Button = ({
  variant = "primary",
  size = "md",
  children,
  ...props
}: React.ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: "primary" | "secondary" | "danger" | "ghost";
  size?: "sm" | "md" | "lg";
}) => {
  const base = "font-medium rounded-md transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2";
  const variants = {
    primary: "bg-indigo-600 text-white hover:bg-indigo-700 focus-visible:ring-indigo-500",
    secondary: "bg-gray-200 text-gray-900 hover:bg-gray-300 focus-visible:ring-gray-500",
    danger: "bg-red-600 text-white hover:bg-red-700 focus-visible:ring-red-500",
    ghost: "text-gray-700 hover:bg-gray-100 focus-visible:ring-gray-500",
  };
  const sizes = {
    sm: "px-2.5 py-1.5 text-xs",
    md: "px-4 py-2 text-sm",
    lg: "px-5 py-2.5 text-base",
  };
  return (
    <button className={`${base} ${variants[variant]} ${sizes[size]}`} {...props}>
      {children}
    </button>
  );
};