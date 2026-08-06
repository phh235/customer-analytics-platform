import Avvvatars from "avvvatars-react"

interface UserAvatarProps {
  email: string
  name: string
  size?: number
}

const getInitials = (name: string) => {
  const parts = name.trim().split(/\s+/).filter(Boolean)

  return parts
    .slice(-2)
    .map((part) => part[0])
    .join("")
    .toUpperCase()
    .slice(0, 2)
}

export function UserAvatar({ email, name, size = 32 }: UserAvatarProps) {
  const avatarValue = email.trim().toLowerCase()
  const initials = getInitials(name)

  return (
    <div
      role="img"
      aria-label={`Ảnh đại diện của ${name}`}
      className="shrink-0"
    >
      <Avvvatars
        value={avatarValue}
        displayValue={initials || avatarValue.slice(0, 2).toUpperCase()}
        size={size}
        style="shape"
      />
    </div>
  )
}
