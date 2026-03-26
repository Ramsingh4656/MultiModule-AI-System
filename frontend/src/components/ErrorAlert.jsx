import React from "react";
import { AlertCircle } from "lucide-react";

const ErrorAlert = ({ title = "Something went wrong", message }) => {
  return (
    <div className="bg-red-500/10 border border-red-500/30 text-red-400 rounded-lg p-4 flex gap-3 items-start">
      <AlertCircle className="mt-0.5" size={18} />
      <div>
        <p className="font-medium">{title}</p>
        {message ? <p className="text-sm mt-1 text-red-300">{message}</p> : null}
      </div>
    </div>
  );
};

export default ErrorAlert;

