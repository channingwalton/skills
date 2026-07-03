Apply fixes for this review report.

Repository root: `{fixture_root}`

Run the focused test from the repository root:

```sh
ruby test/member_search_test.rb
```

```markdown
### Critical (Must Fix)
- `app/queries/member_search.rb:12` SQL injection via interpolated `query`; reproduce with query `%') OR 1=1 --`.

### Warnings (Should Address)
- `app/queries/member_search.rb:1` class name is a bit generic.
- `app/models/member.rb:8` comment restates the method name.

### Suggestions (Nice to Have)
- Consider extracting a search object namespace later.
```

Return the fix report.
