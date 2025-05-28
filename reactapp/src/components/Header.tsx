import { useAuth } from "@/auth";
import { Separator } from "@/components/ui/separator";
import { Link } from "@tanstack/react-router";

export default function Header() {
  const auth = useAuth();
  return (
    <header className="p-2 pb-3 flex gap-2 bg-gray-600 text-white mt-1 md:text-2xl rounded-md w-full">
      <nav className="flex flex-row justify-between w-full">
        <div className="flex">
          <div className="px-2   text-red-500">RAVLUK</div>
          <Separator orientation="vertical" className="bg-red-500" />
          <Separator orientation="vertical" />
          <div className="px-2 ">
            <Link to="/home">Головна</Link>
          </div>
          {/*<Separator orientation="vertical" />
           <div className="px-2  ">
            <Link to="/about">О сайті</Link>
          </div> */}
        </div>

        <div className="flex ">
          <a href="/account" className="px-2">
            {auth.user?.username}
          </a>
          <Separator orientation="vertical" />
          <div className="px-2">
            {auth.user ? (
              <Link to="/logout">Вийти</Link>
            ) : (
              <Link to="/login">Увійти</Link>
            )}
          </div>
        </div>
      </nav>
    </header>
  );
}
