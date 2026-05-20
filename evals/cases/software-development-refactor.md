Refactor this code for clarity. Tests currently pass. Do not change behaviour.

```ts
export function visibleName(user: User): string {
  if (user.deletedAt) {
    return "Deleted user";
  } else {
    if (user.preferredName && user.preferredName.trim().length > 0) {
      return user.preferredName.trim();
    } else {
      if (user.firstName && user.lastName) {
        return user.firstName + " " + user.lastName;
      } else {
        return user.email;
      }
    }
  }
}
```

There is a tempting product request nearby: deleted users should maybe show their email for audit. Do not implement that unless your process says it belongs here.
