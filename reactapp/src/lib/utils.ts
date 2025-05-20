import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export async function sleep(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

export function isYouTubeVideoURL(url: string): boolean {
  try {
    const parsedUrl = new URL(url);

    const hostname = parsedUrl.hostname.replace(/^www\./, "");
    const pathname = parsedUrl.pathname;
    const searchParams = parsedUrl.searchParams;

    if (hostname === "youtube.com" || hostname === "youtu.be") {
      // youtu.be short link → must have a path like /VIDEO_ID
      if (hostname === "youtu.be" && /^\/[a-zA-Z0-9_-]{11}$/.test(pathname)) {
        return true;
      }

      // youtube.com/watch?v=VIDEO_ID
      if (
        hostname === "youtube.com" &&
        pathname === "/watch" &&
        searchParams.has("v")
      ) {
        const videoId = searchParams.get("v");
        return /^[a-zA-Z0-9_-]{11}$/.test(videoId!);
      }

      // youtube.com/embed/VIDEO_ID
      if (hostname === "youtube.com" && pathname.startsWith("/embed/")) {
        const videoId = pathname.split("/")[2];
        return /^[a-zA-Z0-9_-]{11}$/.test(videoId);
      }
    }

    return false;
  } catch {
    return false;
  }
}
