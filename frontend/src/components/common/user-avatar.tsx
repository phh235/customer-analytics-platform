import Avvvatars from "avvvatars-react"

interface UserAvatarProps {
  email: string
}

const getEmailInitials = (email: string) => {
  const localPart = email.split("@")[0] ?? email
  const parts = localPart.split(/[._-]+/).filter(Boolean)

  return (parts.length > 1 ? parts.slice(0, 2) : [localPart.slice(0, 2)])
    .map((part) => part[0])
    .join("")
    .toUpperCase()
    .slice(0, 2)
}

export function UserAvatar({ email }: UserAvatarProps) {
  const avatarValue = email.trim().toLowerCase()
  const initials = getEmailInitials(avatarValue)

  return (
    <span className="inline-flex shrink-0 rounded-full contrast-100 transition-[filter] dark:contrast-125">
      <Avvvatars
        value={avatarValue}
        displayValue={initials || avatarValue.slice(0, 2).toUpperCase()}
        size={32}
        style="shape"
      />
    </span>
  )
}
