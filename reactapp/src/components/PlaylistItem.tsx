import React from "react";
import { Button } from "./ui/button";
import { Label } from "./ui/label";
import {
  Check,
  Edit,
  EllipsisVertical,
  LibraryBig,
  Play,
  Trash,
  X,
} from "lucide-react";
import PlaylistService from "@/APIs/PlaylistService";
import { Input } from "./ui/input";
import useWindowDimensions from "@/hooks/useWindowDimensions";

import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
type Props = {
  playlist_title: string;
  playlist_id: string;
  amount: number;
};

const PlaylistItem: React.FC<Props> = ({
  playlist_title,
  playlist_id,
  amount,
}) => {
  const { height, width } = useWindowDimensions();
  const [edit, setEdit] = React.useState(false);
  const [plst, setPlst] = React.useState({
    title: playlist_title,
    id: playlist_id,
    amount: amount,
  });
  const [input, setInput] = React.useState(plst.title);

  const onClick = () => {
    setEdit(!edit);
  };

  const rename = async (newname: string) => {
    const newPlaylist = await PlaylistService.renamePlaylist(newname, plst.id);
    if (newPlaylist) {
      setPlst({ ...plst, title: newPlaylist.name });
    }
    setEdit(false);
  };

  return (
    <div className="flex justify-self-center justify-between mt-2 md:mt-4 w-[98%]">
      {edit ? (
        <div className="w-[80%] flex items-center">
          <Input
            className="text-xs bg-gray-600  h-9 md:h-14"
            value={input}
            onChange={(event) => setInput(event.target.value)}
          />
          <Button
            variant={"ghost"}
            className="bg-gray-600  h-9 md:h-14 ml-2 md:ml-4 rounded-xl w-[6%] flex justify-center items-center"
            onClick={() => rename(input)}
          >
            <Check size={40} strokeWidth={3} />
          </Button>
        </div>
      ) : (
        <div className="text-xs md:text-xl w-[80%] bg-gray-600  h-9 md:h-14 rounded-xl flex items-center p-2 truncate">
          <a
            href={"/playpage?p=" + playlist_id}
            className="w-[6%] mr-2 md:mr-4 rounded-xl"
          >
            {plst.title}
          </a>
        </div>
      )}

      <Label className="text-sm md:text-xl bg-gray-600 ml-2 md:ml-4 rounded-xl w-[12%] flex justify-center items-center px-4">
        {plst.amount}
        {width > 650 && <LibraryBig size={24} strokeWidth={1.5} />}
      </Label>
      <div>
        <DropdownMenu>
          <DropdownMenuTrigger className="w-10 h-full flex justify-center items-center">
            <EllipsisVertical size={20} />
          </DropdownMenuTrigger>
          <DropdownMenuContent className="bg-gray-600 text-white">
            <DropdownMenuItem
              className="flex justify-center "
              onClick={onClick}
            >
              {edit ? (
                <X size={32} color="white" />
              ) : (
                <Edit color="white" strokeWidth={3} size={40} />
              )}
            </DropdownMenuItem>
            <DropdownMenuItem className="flex justify-center bg-red-600 ">
              <Trash color="white" size={80} strokeWidth={3} />
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </div>
  );
};

export default PlaylistItem;
