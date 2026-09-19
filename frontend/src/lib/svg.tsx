import type { ImgHTMLAttributes, SVGProps } from "react"

import azukiLogo from "@/assets/azuki-logo-primary.png"

export function Brightness(props: SVGProps<SVGSVGElement>) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      {...props}
    >
      <path stroke="none" d="M0 0h24v24H0z" fill="none" />
      <path d="M3 12a9 9 0 1 0 18 0a9 9 0 1 0 -18 0" />
      <path d="M12 3l0 18" />
      <path d="M12 9l4.65 -4.65" />
      <path d="M12 14.3l7.37 -7.37" />
      <path d="M12 19.6l8.85 -8.85" />
    </svg>
  )
}

export function MainLogo({
  alt = "",
  draggable = false,
  ...props
}: ImgHTMLAttributes<HTMLImageElement>) {
  return (
    <img
      src={azukiLogo}
      alt={alt}
      draggable={draggable}
      width="50"
      height="50"
      {...props}
    />
  )
}
