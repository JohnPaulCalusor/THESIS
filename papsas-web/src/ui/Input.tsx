// src/ui/Input.tsx
import React from "react";

const Input = React.forwardRef<HTMLInputElement, React.InputHTMLAttributes<HTMLInputElement>>(
  ({ className, ...props }, ref) => (
    <input
      ref={ref}
      className={`block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm ${className ?? ""}`}
      {...props}
    />
  )
);

Input.displayName = "Input"; // Recommended for debugging

export { Input };