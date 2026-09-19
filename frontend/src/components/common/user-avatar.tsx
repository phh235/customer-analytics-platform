import Avvvatars from "avvvatars-react"

interface UserAvatarProps {
  email?: string
  name?: string
  value?: string
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

const getNameInitials = (name: string) => {
  const parts = name.trim().split(/\s+/).filter(Boolean)
  return [parts[0], parts.at(-1)]
    .filter(Boolean)
    .map((part) => part![0])
    .join("")
    .toUpperCase()
    .slice(0, 2)
}

export function UserAvatar({ email, name, value }: UserAvatarProps) {
  const avatarValue = (value ?? name ?? email ?? "user").trim().toLowerCase()
  const initials = name ? getNameInitials(name) : getEmailInitials(avatarValue)

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
