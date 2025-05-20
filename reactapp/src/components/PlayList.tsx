import React from "react";

import Track from "../components/Track";
import { Input } from "./ui/input";
import { Search } from "lucide-react";
import Recommendations from "./Recomendations";
import { NowPlayContext } from "@/routes/playpage";
import useWindowDimensions from "@/hooks/useWindowDimensions";
import TrackMini from "./TrackMini";

const PlayList: React.FC = () => {
  const [filter, setFilter] = React.useState("");
  const context = React.useContext(NowPlayContext);
  const { height, width } = useWindowDimensions();

  return (
    <div className="PostList">
      <div className="flex gap-2 w-full">
        <Search size={32} />
        <Input
          placeholder="Пошук за назвою або виконавцем"
          onChange={(e) => setFilter(e.target.value)}
        />
      </div>

      {width > 650
        ? context.playlistContent
            .filter(
              (track) =>
                track.title.toLowerCase().includes(filter.toLowerCase()) ||
                track.artist.toLowerCase().includes(filter.toLowerCase())
            )
            .map((track) => (
              <Track key={track.id} track={track} for_w="playlist" />
            ))
        : context.playlistContent
            .filter(
              (track) =>
                track.title.toLowerCase().includes(filter.toLowerCase()) ||
                track.artist.toLowerCase().includes(filter.toLowerCase())
            )
            .map((track) => (
              <TrackMini key={track.id} track={track} for_w="playlist" />
            ))}
      <div className="w-full">
        <Recommendations />
      </div>
      {/* <Track
        track={{
          id: "123321",
          title:
            "From The Ashes - DOOM: The Dark Ages (Original Game Soundtrack) OFFICIAL",
          video_id: "uq8sf6ZK0xY",
          length: 372,
        }}
      />
      <Track
        track={{
          id: "123321",
          title:
            "From The Ashes - DOOM: The Dark Ages (Original Game Soundtrack) OFFICIAL",
          video_id: "uq8sf6ZK0xY",
          length: 372,
        }}
      />
      <Track
        track={{
          id: "123321",
          title:
            "From The Ashes - DOOM: The Dark Ages (Original Game Soundtrack) OFFICIAL",
          video_id: "uq8sf6ZK0xY",
          length: 372,
        }}
      />
      <Track
        track={{
          id: "123321",
          title:
            "From The Ashes - DOOM: The Dark Ages (Original Game Soundtrack) OFFICIAL",
          video_id: "uq8sf6ZK0xY",
          length: 372,
        }}
      /> */}
    </div>
  );
};

export default PlayList;
