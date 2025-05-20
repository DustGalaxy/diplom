import React from "react";

import Track from "@/components/Track";
import PlaylistService, { type TrackData } from "@/APIs/PlaylistService";
import { NowPlayContext } from "@/routes/playpage";
import { Button } from "./ui/button";
import useWindowDimensions from "@/hooks/useWindowDimensions";
import TrackMini from "./TrackMini";

function Recommendations() {
  const context = React.useContext(NowPlayContext);
  const { height, width } = useWindowDimensions();
  const [recommendContent, setRecommendContent] = React.useState<TrackData[]>(
    []
  );

  const onClickreload = async () => {
    const recs = await PlaylistService.getRecommendations(context.playlist_id);
    if (recs) {
      setRecommendContent(recs);
    }
  };

  return (
    <div className="">
      <div className="m-4 flex">
        <h2 className="text-md md:text-2xl">Рекомендації для плейлісту</h2>
        <Button
          onClick={onClickreload}
          variant={"ghost"}
          className="ml-4 bg-gray-600"
        >
          Завантажити
        </Button>
      </div>
      {width > 650
        ? recommendContent?.map((track) => (
            <Track track={track} for_w="recommendations" />
          ))
        : recommendContent?.map((track) => (
            <TrackMini track={track} for_w="recommendations" />
          ))}
    </div>
  );
}

export default Recommendations;
