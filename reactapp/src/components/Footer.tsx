import { Link } from "@tanstack/react-router";
import { Label } from "./ui/label";

export default function Footer() {
  return (
    <footer className="p-2 pb-3 mt-5 flex gap-2 bg-gray-600 text-white md:text-2xl rounded-md w-full">
      <nav className="w-full">
        <div className="flex w-full  justify-between">
          <Link to="/about">О сайті</Link>
          <Label className="md:text-xl text-base">
            All rights reserved © 2025
          </Label>
        </div>
      </nav>
    </footer>
  );
}
