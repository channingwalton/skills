Review this diff. Return findings only; do not edit files.

```diff
diff --git a/app/models/subscription.rb b/app/models/subscription.rb
@@
+  def active_on?(date)
+    starts_at <= date.to_time && ends_at >= date.to_time
+  end
diff --git a/app/queries/member_search.rb b/app/queries/member_search.rb
@@
+  def call(query)
+    Member.where("name ILIKE '%#{query}%'")
+  end
diff --git a/db/migrate/20260520120000_add_member_id_to_events.rb b/db/migrate/20260520120000_add_member_id_to_events.rb
@@
+  def change
+    add_column :events, :member_id, :bigint, null: false
+  end
```
