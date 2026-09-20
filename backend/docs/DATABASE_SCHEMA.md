# PostgreSQL database schema

> Generated from the live local PostgreSQL database (`public` schema).
> This file describes the current database structure, not a migration plan.

- Generated at: `2026-09-18T16:17:52+00:00`
- Tables: **35**
- Columns: **402**
- Constraints: **100**
- Indexes: **105**

## Table index

| Table | Columns | Constraints | Indexes |
|---|---:|---:|---:|
| `alembic_version` | 1 | 1 | 1 |
| `analysis_runs` | 18 | 5 | 2 |
| `audit_logs` | 10 | 2 | 3 |
| `campaigns` | 12 | 2 | 2 |
| `configuration_versions` | 9 | 3 | 2 |
| `customer_assignments` | 6 | 4 | 3 |
| `customer_behavior_history` | 12 | 3 | 1 |
| `customer_interactions` | 14 | 5 | 6 |
| `customer_potential_score_history` | 12 | 4 | 1 |
| `customer_product_preferences` | 14 | 4 | 1 |
| `customers` | 27 | 4 | 9 |
| `employees` | 11 | 3 | 4 |
| `geolocations` | 9 | 2 | 2 |
| `import_errors` | 7 | 2 | 2 |
| `import_jobs` | 17 | 2 | 3 |
| `ml_model_evaluations` | 15 | 2 | 1 |
| `model_registry` | 23 | 2 | 4 |
| `order_items` | 14 | 4 | 4 |
| `orders` | 28 | 5 | 7 |
| `payments` | 10 | 3 | 3 |
| `permissions` | 5 | 1 | 2 |
| `products` | 21 | 1 | 6 |
| `purchase_predictions` | 14 | 4 | 4 |
| `refresh_tokens` | 10 | 2 | 5 |
| `reviews` | 12 | 5 | 4 |
| `role_permissions` | 2 | 3 | 1 |
| `roles` | 4 | 1 | 2 |
| `scoring_rules` | 5 | 3 | 2 |
| `scoring_thresholds` | 7 | 2 | 1 |
| `segment_history` | 11 | 4 | 5 |
| `segmentation_rules` | 7 | 2 | 1 |
| `sellers` | 9 | 2 | 2 |
| `teams` | 7 | 1 | 2 |
| `users` | 15 | 4 | 5 |
| `valid_order_status_configs` | 4 | 3 | 2 |

## `alembic_version`

### Columns

| # | Column | Type | Null | Default |
|---:|---|---|:---:|---|
| 1 | `version_num` | `character varying(32)` | NO | `` |

### Constraints

| Name | Type | Definition |
|---|---|---|
| `alembic_version_pkc` | PRIMARY KEY | `PRIMARY KEY (version_num)` |

### Indexes

| Name | Definition |
|---|---|
| `alembic_version_pkc` | `CREATE UNIQUE INDEX alembic_version_pkc ON public.alembic_version USING btree (version_num)` |

## `analysis_runs`

### Columns

| # | Column | Type | Null | Default |
|---:|---|---|:---:|---|
| 1 | `id` | `uuid` | NO | `` |
| 2 | `created_at` | `timestamp with time zone` | NO | `now()` |
| 3 | `updated_at` | `timestamp with time zone` | NO | `now()` |
| 4 | `run_code` | `character varying(100)` | NO | `` |
| 5 | `analysis_type` | `character varying(50)` | NO | `` |
| 6 | `status` | `character varying(20)` | NO | `'PENDING'::character varying` |
| 7 | `analysis_date` | `date` | NO | `` |
| 8 | `data_from` | `date` | YES | `` |
| 9 | `data_to` | `date` | YES | `` |
| 10 | `started_at` | `timestamp with time zone` | YES | `` |
| 11 | `completed_at` | `timestamp with time zone` | YES | `` |
| 12 | `executed_by` | `uuid` | YES | `` |
| 13 | `configuration_version_id` | `uuid` | YES | `` |
| 14 | `model_version_id` | `uuid` | YES | `` |
| 15 | `total_records` | `integer` | NO | `0` |
| 16 | `success_records` | `integer` | NO | `0` |
| 17 | `failed_records` | `integer` | NO | `0` |
| 18 | `error_message` | `text` | YES | `` |

### Constraints

| Name | Type | Definition |
|---|---|---|
| `fk_analysis_runs_configuration_version_id_configuration_18f6` | FOREIGN KEY | `FOREIGN KEY (configuration_version_id) REFERENCES configuration_versions(id) ON DELETE SET NULL` |
| `fk_analysis_runs_executed_by_users` | FOREIGN KEY | `FOREIGN KEY (executed_by) REFERENCES users(id) ON DELETE SET NULL` |
| `fk_analysis_runs_model_version_id_model_registry` | FOREIGN KEY | `FOREIGN KEY (model_version_id) REFERENCES model_registry(id) ON DELETE SET NULL` |
| `pk_analysis_runs` | PRIMARY KEY | `PRIMARY KEY (id)` |
| `uq_analysis_runs_run_code` | UNIQUE | `UNIQUE (run_code)` |

### Indexes

| Name | Definition |
|---|---|
| `pk_analysis_runs` | `CREATE UNIQUE INDEX pk_analysis_runs ON public.analysis_runs USING btree (id)` |
| `uq_analysis_runs_run_code` | `CREATE UNIQUE INDEX uq_analysis_runs_run_code ON public.analysis_runs USING btree (run_code)` |

## `audit_logs`

### Columns

| # | Column | Type | Null | Default |
|---:|---|---|:---:|---|
| 1 | `id` | `uuid` | NO | `` |
| 2 | `created_at` | `timestamp with time zone` | NO | `now()` |
| 3 | `updated_at` | `timestamp with time zone` | NO | `now()` |
| 4 | `actor_id` | `uuid` | YES | `` |
| 5 | `action` | `character varying(100)` | NO | `` |
| 6 | `entity_type` | `character varying(100)` | NO | `` |
| 7 | `entity_id` | `character varying(100)` | YES | `` |
| 8 | `before_data` | `json` | YES | `` |
| 9 | `after_data` | `json` | YES | `` |
| 10 | `ip_address` | `character varying(45)` | YES | `` |

### Constraints

| Name | Type | Definition |
|---|---|---|
| `fk_audit_logs_actor_id_users` | FOREIGN KEY | `FOREIGN KEY (actor_id) REFERENCES users(id) ON DELETE SET NULL` |
| `pk_audit_logs` | PRIMARY KEY | `PRIMARY KEY (id)` |

### Indexes

| Name | Definition |
|---|---|
| `ix_audit_logs_actor_id` | `CREATE INDEX ix_audit_logs_actor_id ON public.audit_logs USING btree (actor_id)` |
| `ix_audit_logs_entity` | `CREATE INDEX ix_audit_logs_entity ON public.audit_logs USING btree (entity_type, entity_id)` |
| `pk_audit_logs` | `CREATE UNIQUE INDEX pk_audit_logs ON public.audit_logs USING btree (id)` |

## `campaigns`

### Columns

| # | Column | Type | Null | Default |
|---:|---|---|:---:|---|
| 1 | `id` | `uuid` | NO | `` |
| 2 | `created_at` | `timestamp with time zone` | NO | `now()` |
| 3 | `updated_at` | `timestamp with time zone` | NO | `now()` |
| 4 | `campaign_code` | `character varying(50)` | NO | `` |
| 5 | `name` | `character varying(150)` | NO | `` |
| 6 | `campaign_type` | `character varying(50)` | YES | `` |
| 7 | `start_date` | `date` | YES | `` |
| 8 | `end_date` | `date` | YES | `` |
| 9 | `channel` | `character varying(50)` | YES | `` |
| 10 | `target_segment` | `character varying(100)` | YES | `` |
| 11 | `status` | `character varying(20)` | NO | `'ACTIVE'::character varying` |
| 12 | `budget_vnd` | `numeric(14,2)` | YES | `` |

### Constraints

| Name | Type | Definition |
|---|---|---|
| `pk_campaigns` | PRIMARY KEY | `PRIMARY KEY (id)` |
| `uq_campaigns_campaign_code` | UNIQUE | `UNIQUE (campaign_code)` |

### Indexes

| Name | Definition |
|---|---|
| `pk_campaigns` | `CREATE UNIQUE INDEX pk_campaigns ON public.campaigns USING btree (id)` |
| `uq_campaigns_campaign_code` | `CREATE UNIQUE INDEX uq_campaigns_campaign_code ON public.campaigns USING btree (campaign_code)` |

## `configuration_versions`

### Columns

| # | Column | Type | Null | Default |
|---:|---|---|:---:|---|
| 1 | `id` | `uuid` | NO | `` |
| 2 | `created_at` | `timestamp with time zone` | NO | `now()` |
| 3 | `updated_at` | `timestamp with time zone` | NO | `now()` |
| 4 | `version` | `character varying(100)` | NO | `` |
| 5 | `status` | `character varying(20)` | NO | `'ACTIVE'::character varying` |
| 6 | `description` | `character varying(500)` | YES | `` |
| 7 | `effective_from` | `timestamp with time zone` | YES | `` |
| 8 | `effective_to` | `timestamp with time zone` | YES | `` |
| 9 | `created_by` | `uuid` | YES | `` |

### Constraints

| Name | Type | Definition |
|---|---|---|
| `fk_configuration_versions_created_by_users` | FOREIGN KEY | `FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL` |
| `pk_configuration_versions` | PRIMARY KEY | `PRIMARY KEY (id)` |
| `uq_configuration_versions_version` | UNIQUE | `UNIQUE (version)` |

### Indexes

| Name | Definition |
|---|---|
| `pk_configuration_versions` | `CREATE UNIQUE INDEX pk_configuration_versions ON public.configuration_versions USING btree (id)` |
| `uq_configuration_versions_version` | `CREATE UNIQUE INDEX uq_configuration_versions_version ON public.configuration_versions USING btree (version)` |

## `customer_assignments`

### Columns

| # | Column | Type | Null | Default |
|---:|---|---|:---:|---|
| 1 | `id` | `uuid` | NO | `` |
| 2 | `customer_id` | `uuid` | NO | `` |
| 3 | `user_id` | `uuid` | NO | `` |
| 4 | `assigned_at` | `timestamp with time zone` | NO | `now()` |
| 5 | `assigned_by` | `uuid` | YES | `` |
| 6 | `active` | `boolean` | NO | `true` |

### Constraints

| Name | Type | Definition |
|---|---|---|
| `fk_customer_assignments_assigned_by_users` | FOREIGN KEY | `FOREIGN KEY (assigned_by) REFERENCES users(id) ON DELETE SET NULL` |
| `fk_customer_assignments_customer_id_customers` | FOREIGN KEY | `FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE` |
| `fk_customer_assignments_user_id_users` | FOREIGN KEY | `FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE` |
| `pk_customer_assignments` | PRIMARY KEY | `PRIMARY KEY (id)` |

### Indexes

| Name | Definition |
|---|---|
| `ix_customer_assignments_customer_id` | `CREATE INDEX ix_customer_assignments_customer_id ON public.customer_assignments USING btree (customer_id)` |
| `ix_customer_assignments_user_id` | `CREATE INDEX ix_customer_assignments_user_id ON public.customer_assignments USING btree (user_id)` |
| `pk_customer_assignments` | `CREATE UNIQUE INDEX pk_customer_assignments ON public.customer_assignments USING btree (id)` |

## `customer_behavior_history`

### Columns

| # | Column | Type | Null | Default |
|---:|---|---|:---:|---|
| 1 | `id` | `uuid` | NO | `` |
| 2 | `created_at` | `timestamp with time zone` | NO | `now()` |
| 3 | `updated_at` | `timestamp with time zone` | NO | `now()` |
| 4 | `analysis_run_id` | `uuid` | NO | `` |
| 5 | `customer_id` | `uuid` | NO | `` |
| 6 | `recency_days` | `integer` | YES | `` |
| 7 | `frequency` | `integer` | NO | `` |
| 8 | `monetary` | `numeric(12,2)` | NO | `` |
| 9 | `aov` | `numeric(12,2)` | NO | `` |
| 10 | `avg_purchase_cycle_days` | `numeric(12,2)` | YES | `` |
| 11 | `trend` | `character varying(30)` | YES | `` |
| 12 | `avg_review_score` | `numeric(5,2)` | YES | `` |

### Constraints

| Name | Type | Definition |
|---|---|---|
| `fk_customer_behavior_history_analysis_run_id_analysis_runs` | FOREIGN KEY | `FOREIGN KEY (analysis_run_id) REFERENCES analysis_runs(id) ON DELETE CASCADE` |
| `fk_customer_behavior_history_customer_id_customers` | FOREIGN KEY | `FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE` |
| `pk_customer_behavior_history` | PRIMARY KEY | `PRIMARY KEY (id)` |

### Indexes

| Name | Definition |
|---|---|
| `pk_customer_behavior_history` | `CREATE UNIQUE INDEX pk_customer_behavior_history ON public.customer_behavior_history USING btree (id)` |

## `customer_interactions`

### Columns

| # | Column | Type | Null | Default |
|---:|---|---|:---:|---|
| 1 | `id` | `uuid` | NO | `` |
| 2 | `created_at` | `timestamp with time zone` | NO | `now()` |
| 3 | `updated_at` | `timestamp with time zone` | NO | `now()` |
| 4 | `interaction_code` | `character varying(100)` | YES | `` |
| 5 | `customer_id` | `uuid` | NO | `` |
| 6 | `product_id` | `uuid` | NO | `` |
| 7 | `campaign_id` | `uuid` | YES | `` |
| 8 | `interaction_type` | `character varying(50)` | NO | `` |
| 9 | `interaction_timestamp` | `timestamp with time zone` | NO | `` |
| 10 | `channel` | `character varying(50)` | YES | `` |
| 11 | `session_id` | `character varying(100)` | YES | `` |
| 12 | `interaction_value` | `numeric(10,4)` | NO | `'0'::numeric` |
| 13 | `interaction_result` | `character varying(100)` | YES | `` |
| 14 | `is_mock_data` | `boolean` | NO | `true` |

### Constraints

| Name | Type | Definition |
|---|---|---|
| `fk_customer_interactions_campaign_id_campaigns` | FOREIGN KEY | `FOREIGN KEY (campaign_id) REFERENCES campaigns(id) ON DELETE SET NULL` |
| `fk_customer_interactions_customer_id_customers` | FOREIGN KEY | `FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE` |
| `fk_customer_interactions_product_id_products` | FOREIGN KEY | `FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE` |
| `pk_customer_interactions` | PRIMARY KEY | `PRIMARY KEY (id)` |
| `uq_customer_interactions_interaction_code` | UNIQUE | `UNIQUE (interaction_code)` |

### Indexes

| Name | Definition |
|---|---|
| `ix_customer_interactions_campaign_id` | `CREATE INDEX ix_customer_interactions_campaign_id ON public.customer_interactions USING btree (campaign_id)` |
| `ix_customer_interactions_customer_id` | `CREATE INDEX ix_customer_interactions_customer_id ON public.customer_interactions USING btree (customer_id)` |
| `ix_customer_interactions_product_id` | `CREATE INDEX ix_customer_interactions_product_id ON public.customer_interactions USING btree (product_id)` |
| `ix_customer_interactions_timestamp` | `CREATE INDEX ix_customer_interactions_timestamp ON public.customer_interactions USING btree (interaction_timestamp)` |
| `pk_customer_interactions` | `CREATE UNIQUE INDEX pk_customer_interactions ON public.customer_interactions USING btree (id)` |
| `uq_customer_interactions_interaction_code` | `CREATE UNIQUE INDEX uq_customer_interactions_interaction_code ON public.customer_interactions USING btree (interaction_code)` |

## `customer_potential_score_history`

### Columns

| # | Column | Type | Null | Default |
|---:|---|---|:---:|---|
| 1 | `id` | `uuid` | NO | `` |
| 2 | `created_at` | `timestamp with time zone` | NO | `now()` |
| 3 | `updated_at` | `timestamp with time zone` | NO | `now()` |
| 4 | `analysis_run_id` | `uuid` | NO | `` |
| 5 | `customer_id` | `uuid` | NO | `` |
| 6 | `r_score` | `numeric(6,2)` | YES | `` |
| 7 | `f_score` | `numeric(6,2)` | YES | `` |
| 8 | `m_score` | `numeric(6,2)` | YES | `` |
| 9 | `interaction_score` | `numeric(6,2)` | NO | `'0'::numeric` |
| 10 | `potential_score` | `numeric(6,2)` | YES | `` |
| 11 | `potential_level` | `character varying(30)` | NO | `` |
| 12 | `configuration_version_id` | `uuid` | YES | `` |

### Constraints

| Name | Type | Definition |
|---|---|---|
| `fk_customer_potential_score_history_analysis_run_id_ana_ed2e` | FOREIGN KEY | `FOREIGN KEY (analysis_run_id) REFERENCES analysis_runs(id) ON DELETE CASCADE` |
| `fk_customer_potential_score_history_configuration_versi_9a3c` | FOREIGN KEY | `FOREIGN KEY (configuration_version_id) REFERENCES configuration_versions(id) ON DELETE SET NULL` |
| `fk_customer_potential_score_history_customer_id_customers` | FOREIGN KEY | `FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE` |
| `pk_customer_potential_score_history` | PRIMARY KEY | `PRIMARY KEY (id)` |

### Indexes

| Name | Definition |
|---|---|
| `pk_customer_potential_score_history` | `CREATE UNIQUE INDEX pk_customer_potential_score_history ON public.customer_potential_score_history USING btree (id)` |

## `customer_product_preferences`

### Columns

| # | Column | Type | Null | Default |
|---:|---|---|:---:|---|
| 1 | `id` | `uuid` | NO | `` |
| 2 | `created_at` | `timestamp with time zone` | NO | `now()` |
| 3 | `updated_at` | `timestamp with time zone` | NO | `now()` |
| 4 | `analysis_run_id` | `uuid` | NO | `` |
| 5 | `customer_id` | `uuid` | NO | `` |
| 6 | `product_id` | `uuid` | YES | `` |
| 7 | `product_category_name` | `character varying(100)` | NO | `` |
| 8 | `rank` | `integer` | NO | `` |
| 9 | `score` | `numeric(12,4)` | NO | `` |
| 10 | `purchase_frequency` | `integer` | NO | `0` |
| 11 | `quantity` | `integer` | NO | `0` |
| 12 | `monetary` | `numeric(12,2)` | NO | `` |
| 13 | `purchase_share` | `numeric(8,5)` | NO | `` |
| 14 | `last_purchase_at` | `timestamp with time zone` | YES | `` |

### Constraints

| Name | Type | Definition |
|---|---|---|
| `fk_customer_product_preferences_analysis_run_id_analysis_runs` | FOREIGN KEY | `FOREIGN KEY (analysis_run_id) REFERENCES analysis_runs(id) ON DELETE CASCADE` |
| `fk_customer_product_preferences_customer_id_customers` | FOREIGN KEY | `FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE` |
| `fk_customer_product_preferences_product_id_products` | FOREIGN KEY | `FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE SET NULL` |
| `pk_customer_product_preferences` | PRIMARY KEY | `PRIMARY KEY (id)` |

### Indexes

| Name | Definition |
|---|---|
| `pk_customer_product_preferences` | `CREATE UNIQUE INDEX pk_customer_product_preferences ON public.customer_product_preferences USING btree (id)` |

## `customers`

### Columns

| # | Column | Type | Null | Default |
|---:|---|---|:---:|---|
| 1 | `id` | `uuid` | NO | `` |
| 2 | `name` | `character varying(100)` | NO | `` |
| 3 | `email` | `character varying(255)` | YES | `` |
| 4 | `phone` | `character varying(20)` | YES | `` |
| 5 | `address` | `character varying(255)` | YES | `` |
| 6 | `status` | `character varying(20)` | NO | `'ACTIVE'::character varying` |
| 7 | `gender` | `character varying(10)` | YES | `` |
| 8 | `date_of_birth` | `date` | YES | `` |
| 9 | `region` | `character varying(50)` | YES | `` |
| 10 | `customer_since` | `timestamp with time zone` | YES | `` |
| 11 | `total_orders` | `integer` | NO | `0` |
| 12 | `total_spent` | `numeric(12,2)` | NO | `'0'::numeric` |
| 13 | `avg_order_value` | `numeric(10,2)` | NO | `'0'::numeric` |
| 14 | `last_purchase_date` | `timestamp with time zone` | YES | `` |
| 15 | `created_at` | `timestamp with time zone` | NO | `now()` |
| 16 | `updated_at` | `timestamp with time zone` | NO | `now()` |
| 17 | `assigned_user_id` | `uuid` | YES | `` |
| 18 | `team_id` | `uuid` | YES | `` |
| 19 | `customer_code` | `character varying(50)` | YES | `` |
| 20 | `source_customer_id` | `character varying(100)` | YES | `` |
| 21 | `zip_code` | `character varying(20)` | YES | `` |
| 22 | `city` | `character varying(100)` | YES | `` |
| 23 | `state_code` | `character varying(20)` | YES | `` |
| 24 | `province_city` | `character varying(150)` | YES | `` |
| 25 | `registered_at` | `timestamp with time zone` | YES | `` |
| 26 | `owner_id` | `uuid` | YES | `` |
| 27 | `is_deleted` | `boolean` | NO | `false` |

### Constraints

| Name | Type | Definition |
|---|---|---|
| `fk_customers_assigned_user_id_users` | FOREIGN KEY | `FOREIGN KEY (assigned_user_id) REFERENCES users(id) ON DELETE SET NULL` |
| `fk_customers_owner_id_employees` | FOREIGN KEY | `FOREIGN KEY (owner_id) REFERENCES employees(id) ON DELETE SET NULL` |
| `fk_customers_team_id_teams` | FOREIGN KEY | `FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE SET NULL` |
| `pk_customers` | PRIMARY KEY | `PRIMARY KEY (id)` |

### Indexes

| Name | Definition |
|---|---|
| `ix_customers_assigned_user_id` | `CREATE INDEX ix_customers_assigned_user_id ON public.customers USING btree (assigned_user_id)` |
| `ix_customers_customer_code` | `CREATE UNIQUE INDEX ix_customers_customer_code ON public.customers USING btree (customer_code)` |
| `ix_customers_email` | `CREATE UNIQUE INDEX ix_customers_email ON public.customers USING btree (email)` |
| `ix_customers_owner_id` | `CREATE INDEX ix_customers_owner_id ON public.customers USING btree (owner_id)` |
| `ix_customers_phone` | `CREATE UNIQUE INDEX ix_customers_phone ON public.customers USING btree (phone)` |
| `ix_customers_region` | `CREATE INDEX ix_customers_region ON public.customers USING btree (region)` |
| `ix_customers_source_customer_id` | `CREATE UNIQUE INDEX ix_customers_source_customer_id ON public.customers USING btree (source_customer_id)` |
| `ix_customers_team_id` | `CREATE INDEX ix_customers_team_id ON public.customers USING btree (team_id)` |
| `pk_customers` | `CREATE UNIQUE INDEX pk_customers ON public.customers USING btree (id)` |

## `employees`

### Columns

| # | Column | Type | Null | Default |
|---:|---|---|:---:|---|
| 1 | `id` | `uuid` | NO | `` |
| 2 | `created_at` | `timestamp with time zone` | NO | `now()` |
| 3 | `updated_at` | `timestamp with time zone` | NO | `now()` |
| 4 | `employee_code` | `character varying(50)` | NO | `` |
| 5 | `name` | `character varying(150)` | NO | `` |
| 6 | `department` | `character varying(100)` | YES | `` |
| 7 | `email` | `character varying(255)` | YES | `` |
| 8 | `phone` | `character varying(30)` | YES | `` |
| 9 | `region_scope` | `character varying(100)` | YES | `` |
| 10 | `status` | `character varying(20)` | NO | `'ACTIVE'::character varying` |
| 11 | `start_date` | `date` | YES | `` |

### Constraints

| Name | Type | Definition |
|---|---|---|
| `pk_employees` | PRIMARY KEY | `PRIMARY KEY (id)` |
| `uq_employees_email` | UNIQUE | `UNIQUE (email)` |
| `uq_employees_employee_code` | UNIQUE | `UNIQUE (employee_code)` |

### Indexes

| Name | Definition |
|---|---|
| `ix_employees_status` | `CREATE INDEX ix_employees_status ON public.employees USING btree (status)` |
| `pk_employees` | `CREATE UNIQUE INDEX pk_employees ON public.employees USING btree (id)` |
| `uq_employees_email` | `CREATE UNIQUE INDEX uq_employees_email ON public.employees USING btree (email)` |
| `uq_employees_employee_code` | `CREATE UNIQUE INDEX uq_employees_employee_code ON public.employees USING btree (employee_code)` |

## `geolocations`

### Columns

| # | Column | Type | Null | Default |
|---:|---|---|:---:|---|
| 1 | `id` | `uuid` | NO | `` |
| 2 | `created_at` | `timestamp with time zone` | NO | `now()` |
| 3 | `updated_at` | `timestamp with time zone` | NO | `now()` |
| 4 | `zip_code` | `character varying(20)` | NO | `` |
| 5 | `latitude` | `numeric(10,7)` | YES | `` |
| 6 | `longitude` | `numeric(10,7)` | YES | `` |
| 7 | `city` | `character varying(100)` | YES | `` |
| 8 | `state_code` | `character varying(20)` | YES | `` |
| 9 | `region` | `character varying(100)` | YES | `` |

### Constraints

| Name | Type | Definition |
|---|---|---|
| `pk_geolocations` | PRIMARY KEY | `PRIMARY KEY (id)` |
| `uq_geolocations_zip_code` | UNIQUE | `UNIQUE (zip_code)` |

### Indexes

| Name | Definition |
|---|---|
| `pk_geolocations` | `CREATE UNIQUE INDEX pk_geolocations ON public.geolocations USING btree (id)` |
| `uq_geolocations_zip_code` | `CREATE UNIQUE INDEX uq_geolocations_zip_code ON public.geolocations USING btree (zip_code)` |

## `import_errors`

### Columns

| # | Column | Type | Null | Default |
|---:|---|---|:---:|---|
| 1 | `id` | `uuid` | NO | `` |
| 2 | `import_job_id` | `uuid` | NO | `` |
| 3 | `row_number` | `integer` | NO | `` |
| 4 | `field_name` | `character varying(100)` | YES | `` |
| 5 | `error_code` | `character varying(100)` | NO | `` |
| 6 | `error_message` | `text` | NO | `` |
| 7 | `raw_value` | `text` | YES | `` |

### Constraints

| Name | Type | Definition |
|---|---|---|
| `fk_import_errors_import_job_id_import_jobs` | FOREIGN KEY | `FOREIGN KEY (import_job_id) REFERENCES import_jobs(id) ON DELETE CASCADE` |
| `pk_import_errors` | PRIMARY KEY | `PRIMARY KEY (id)` |

### Indexes

| Name | Definition |
|---|---|
| `ix_import_errors_import_job_id` | `CREATE INDEX ix_import_errors_import_job_id ON public.import_errors USING btree (import_job_id)` |
| `pk_import_errors` | `CREATE UNIQUE INDEX pk_import_errors ON public.import_errors USING btree (id)` |

## `import_jobs`

### Columns

| # | Column | Type | Null | Default |
|---:|---|---|:---:|---|
| 1 | `id` | `uuid` | NO | `` |
| 2 | `filename` | `character varying(255)` | NO | `` |
| 3 | `import_type` | `character varying(50)` | NO | `` |
| 4 | `status` | `character varying(20)` | NO | `'PENDING'::character varying` |
| 5 | `total_rows` | `integer` | NO | `0` |
| 6 | `processed_rows` | `integer` | NO | `0` |
| 7 | `success_rows` | `integer` | NO | `0` |
| 8 | `error_rows` | `integer` | NO | `0` |
| 9 | `errors` | `json` | YES | `` |
| 10 | `mapping` | `json` | YES | `` |
| 11 | `created_by` | `uuid` | YES | `` |
| 12 | `completed_at` | `timestamp with time zone` | YES | `` |
| 13 | `storage_key` | `character varying(500)` | YES | `` |
| 14 | `file_sha256` | `character varying(64)` | YES | `` |
| 15 | `file_size` | `integer` | YES | `` |
| 16 | `created_at` | `timestamp with time zone` | NO | `now()` |
| 17 | `updated_at` | `timestamp with time zone` | NO | `now()` |

### Constraints

| Name | Type | Definition |
|---|---|---|
| `fk_import_jobs_created_by_users` | FOREIGN KEY | `FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL` |
| `pk_import_jobs` | PRIMARY KEY | `PRIMARY KEY (id)` |

### Indexes

| Name | Definition |
|---|---|
| `ix_import_jobs_import_type` | `CREATE INDEX ix_import_jobs_import_type ON public.import_jobs USING btree (import_type)` |
| `ix_import_jobs_status` | `CREATE INDEX ix_import_jobs_status ON public.import_jobs USING btree (status)` |
| `pk_import_jobs` | `CREATE UNIQUE INDEX pk_import_jobs ON public.import_jobs USING btree (id)` |

## `ml_model_evaluations`

### Columns

| # | Column | Type | Null | Default |
|---:|---|---|:---:|---|
| 1 | `id` | `uuid` | NO | `` |
| 2 | `created_at` | `timestamp with time zone` | NO | `now()` |
| 3 | `updated_at` | `timestamp with time zone` | NO | `now()` |
| 4 | `model_version_id` | `uuid` | NO | `` |
| 5 | `evaluation_dataset_version` | `character varying(100)` | YES | `` |
| 6 | `precision` | `numeric(10,6)` | YES | `` |
| 7 | `recall` | `numeric(10,6)` | YES | `` |
| 8 | `f1_score` | `numeric(10,6)` | YES | `` |
| 9 | `roc_auc` | `numeric(10,6)` | YES | `` |
| 10 | `pr_auc` | `numeric(10,6)` | YES | `` |
| 11 | `precision_at_k` | `numeric(10,6)` | YES | `` |
| 12 | `recall_at_k` | `numeric(10,6)` | YES | `` |
| 13 | `lift_at_k` | `numeric(10,6)` | YES | `` |
| 14 | `metrics` | `json` | YES | `` |
| 15 | `evaluated_at` | `timestamp with time zone` | NO | `` |

### Constraints

| Name | Type | Definition |
|---|---|---|
| `fk_ml_model_evaluations_model_version_id_model_registry` | FOREIGN KEY | `FOREIGN KEY (model_version_id) REFERENCES model_registry(id) ON DELETE CASCADE` |
| `pk_ml_model_evaluations` | PRIMARY KEY | `PRIMARY KEY (id)` |

### Indexes

| Name | Definition |
|---|---|
| `pk_ml_model_evaluations` | `CREATE UNIQUE INDEX pk_ml_model_evaluations ON public.ml_model_evaluations USING btree (id)` |

## `model_registry`

### Columns

| # | Column | Type | Null | Default |
|---:|---|---|:---:|---|
| 1 | `id` | `uuid` | NO | `` |
| 2 | `created_at` | `timestamp with time zone` | NO | `` |
| 3 | `updated_at` | `timestamp with time zone` | NO | `` |
| 4 | `version` | `character varying(100)` | NO | `` |
| 5 | `status` | `character varying(20)` | NO | `` |
| 6 | `pr_auc` | `numeric(10,6)` | YES | `` |
| 7 | `lift_top10` | `numeric(10,4)` | YES | `` |
| 8 | `precision_top10` | `numeric(10,6)` | YES | `` |
| 9 | `baseline_pr_auc` | `numeric(10,6)` | NO | `` |
| 10 | `metrics` | `json` | YES | `` |
| 11 | `artifact_uri` | `character varying(500)` | YES | `` |
| 12 | `evaluated_at` | `timestamp with time zone` | YES | `` |
| 13 | `model_code` | `character varying(100)` | NO | `'PURCHASE_REPEAT'::character varying` |
| 14 | `model_type` | `character varying(100)` | YES | `` |
| 15 | `dataset_version` | `character varying(100)` | YES | `` |
| 16 | `trained_at` | `timestamp with time zone` | YES | `` |
| 17 | `feature_window_days` | `integer` | YES | `` |
| 18 | `prediction_horizon_days` | `integer` | YES | `` |
| 19 | `precision` | `numeric(10,6)` | YES | `` |
| 20 | `recall` | `numeric(10,6)` | YES | `` |
| 21 | `f1_score` | `numeric(10,6)` | YES | `` |
| 22 | `roc_auc` | `numeric(10,6)` | YES | `` |
| 23 | `notes` | `character varying(1000)` | YES | `` |

### Constraints

| Name | Type | Definition |
|---|---|---|
| `pk_model_registry` | PRIMARY KEY | `PRIMARY KEY (id)` |
| `uq_model_registry_version` | UNIQUE | `UNIQUE (version)` |

### Indexes

| Name | Definition |
|---|---|
| `ix_model_registry_model_code` | `CREATE INDEX ix_model_registry_model_code ON public.model_registry USING btree (model_code)` |
| `ix_model_registry_status` | `CREATE INDEX ix_model_registry_status ON public.model_registry USING btree (status)` |
| `pk_model_registry` | `CREATE UNIQUE INDEX pk_model_registry ON public.model_registry USING btree (id)` |
| `uq_model_registry_version` | `CREATE UNIQUE INDEX uq_model_registry_version ON public.model_registry USING btree (version)` |

## `order_items`

### Columns

| # | Column | Type | Null | Default |
|---:|---|---|:---:|---|
| 1 | `id` | `uuid` | NO | `` |
| 2 | `order_id` | `uuid` | NO | `` |
| 3 | `product_id` | `uuid` | NO | `` |
| 4 | `quantity` | `integer` | NO | `` |
| 5 | `unit_price` | `numeric(10,2)` | NO | `` |
| 6 | `subtotal` | `numeric(10,2)` | NO | `` |
| 7 | `seller_id` | `uuid` | YES | `` |
| 8 | `item_sequence` | `integer` | YES | `` |
| 9 | `freight_value` | `numeric(10,2)` | YES | `` |
| 10 | `discount_value` | `numeric(10,2)` | YES | `` |
| 11 | `line_subtotal` | `numeric(12,2)` | YES | `` |
| 12 | `line_amount` | `numeric(12,2)` | YES | `` |
| 13 | `line_total` | `numeric(12,2)` | YES | `` |
| 14 | `shipping_limit_at` | `timestamp with time zone` | YES | `` |

### Constraints

| Name | Type | Definition |
|---|---|---|
| `fk_order_items_order_id_orders` | FOREIGN KEY | `FOREIGN KEY (order_id) REFERENCES orders(id)` |
| `fk_order_items_product_id_products` | FOREIGN KEY | `FOREIGN KEY (product_id) REFERENCES products(id)` |
| `fk_order_items_seller_id_sellers` | FOREIGN KEY | `FOREIGN KEY (seller_id) REFERENCES sellers(id) ON DELETE SET NULL` |
| `pk_order_items` | PRIMARY KEY | `PRIMARY KEY (id)` |

### Indexes

| Name | Definition |
|---|---|
| `ix_order_items_order_id` | `CREATE INDEX ix_order_items_order_id ON public.order_items USING btree (order_id)` |
| `ix_order_items_product_id` | `CREATE INDEX ix_order_items_product_id ON public.order_items USING btree (product_id)` |
| `ix_order_items_seller_id` | `CREATE INDEX ix_order_items_seller_id ON public.order_items USING btree (seller_id)` |
| `pk_order_items` | `CREATE UNIQUE INDEX pk_order_items ON public.order_items USING btree (id)` |

## `orders`

### Columns

| # | Column | Type | Null | Default |
|---:|---|---|:---:|---|
| 1 | `id` | `uuid` | NO | `` |
| 2 | `customer_id` | `uuid` | NO | `` |
| 3 | `order_number` | `character varying(50)` | NO | `` |
| 4 | `order_date` | `timestamp with time zone` | NO | `` |
| 5 | `total_amount` | `numeric(12,2)` | NO | `` |
| 6 | `status` | `character varying(20)` | NO | `'COMPLETED'::character varying` |
| 7 | `channel` | `character varying(50)` | YES | `` |
| 8 | `notes` | `text` | YES | `` |
| 9 | `created_at` | `timestamp with time zone` | NO | `now()` |
| 10 | `updated_at` | `timestamp with time zone` | NO | `now()` |
| 11 | `refund_amount` | `numeric(12,2)` | NO | `'0'::numeric` |
| 12 | `net_amount` | `numeric(12,2)` | NO | `` |
| 13 | `owner_id` | `uuid` | YES | `` |
| 14 | `source_order_id` | `character varying(100)` | YES | `` |
| 15 | `order_code` | `character varying(100)` | YES | `` |
| 16 | `approved_at` | `timestamp with time zone` | YES | `` |
| 17 | `delivered_carrier_at` | `timestamp with time zone` | YES | `` |
| 18 | `delivered_customer_at` | `timestamp with time zone` | YES | `` |
| 19 | `estimated_delivery_at` | `timestamp with time zone` | YES | `` |
| 20 | `subtotal` | `numeric(12,2)` | YES | `` |
| 21 | `freight_total` | `numeric(12,2)` | YES | `` |
| 22 | `discount_total` | `numeric(12,2)` | YES | `` |
| 23 | `payment_method` | `character varying(50)` | YES | `` |
| 24 | `sales_channel` | `character varying(50)` | YES | `` |
| 25 | `region` | `character varying(100)` | YES | `` |
| 26 | `province_city` | `character varying(150)` | YES | `` |
| 27 | `currency` | `character varying(3)` | NO | `'VND'::character varying` |
| 28 | `is_valid_for_rfm` | `boolean` | NO | `true` |

### Constraints

| Name | Type | Definition |
|---|---|---|
| `ck_orders_ck_orders_net_amount_non_negative` | CHECK | `CHECK ((net_amount >= (0)::numeric))` |
| `ck_orders_ck_orders_refund_amount_valid` | CHECK | `CHECK (((refund_amount >= (0)::numeric) AND (refund_amount <= total_amount)))` |
| `fk_orders_customer_id_customers` | FOREIGN KEY | `FOREIGN KEY (customer_id) REFERENCES customers(id)` |
| `fk_orders_owner_id_employees` | FOREIGN KEY | `FOREIGN KEY (owner_id) REFERENCES employees(id) ON DELETE SET NULL` |
| `pk_orders` | PRIMARY KEY | `PRIMARY KEY (id)` |

### Indexes

| Name | Definition |
|---|---|
| `ix_orders_customer_id` | `CREATE INDEX ix_orders_customer_id ON public.orders USING btree (customer_id)` |
| `ix_orders_order_code` | `CREATE UNIQUE INDEX ix_orders_order_code ON public.orders USING btree (order_code)` |
| `ix_orders_order_date` | `CREATE INDEX ix_orders_order_date ON public.orders USING btree (order_date)` |
| `ix_orders_order_number` | `CREATE UNIQUE INDEX ix_orders_order_number ON public.orders USING btree (order_number)` |
| `ix_orders_owner_id` | `CREATE INDEX ix_orders_owner_id ON public.orders USING btree (owner_id)` |
| `ix_orders_source_order_id` | `CREATE UNIQUE INDEX ix_orders_source_order_id ON public.orders USING btree (source_order_id)` |
| `pk_orders` | `CREATE UNIQUE INDEX pk_orders ON public.orders USING btree (id)` |

## `payments`

### Columns

| # | Column | Type | Null | Default |
|---:|---|---|:---:|---|
| 1 | `id` | `uuid` | NO | `` |
| 2 | `created_at` | `timestamp with time zone` | NO | `now()` |
| 3 | `updated_at` | `timestamp with time zone` | NO | `now()` |
| 4 | `order_id` | `uuid` | NO | `` |
| 5 | `payment_sequence` | `integer` | NO | `` |
| 6 | `payment_type` | `character varying(50)` | YES | `` |
| 7 | `payment_method` | `character varying(50)` | YES | `` |
| 8 | `payment_installments` | `integer` | YES | `` |
| 9 | `payment_value` | `numeric(12,2)` | NO | `` |
| 10 | `currency` | `character varying(3)` | NO | `'VND'::character varying` |

### Constraints

| Name | Type | Definition |
|---|---|---|
| `fk_payments_order_id_orders` | FOREIGN KEY | `FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE` |
| `pk_payments` | PRIMARY KEY | `PRIMARY KEY (id)` |
| `uq_payments_order_sequence` | UNIQUE | `UNIQUE (order_id, payment_sequence)` |

### Indexes

| Name | Definition |
|---|---|
| `ix_payments_order_id` | `CREATE INDEX ix_payments_order_id ON public.payments USING btree (order_id)` |
| `pk_payments` | `CREATE UNIQUE INDEX pk_payments ON public.payments USING btree (id)` |
| `uq_payments_order_sequence` | `CREATE UNIQUE INDEX uq_payments_order_sequence ON public.payments USING btree (order_id, payment_sequence)` |

## `permissions`

### Columns

| # | Column | Type | Null | Default |
|---:|---|---|:---:|---|
| 1 | `code` | `character varying(100)` | NO | `` |
| 2 | `resource` | `character varying(50)` | NO | `` |
| 3 | `action` | `character varying(50)` | NO | `` |
| 4 | `description` | `character varying(255)` | YES | `` |
| 5 | `id` | `uuid` | NO | `` |

### Constraints

| Name | Type | Definition |
|---|---|---|
| `pk_permissions` | PRIMARY KEY | `PRIMARY KEY (id)` |

### Indexes

| Name | Definition |
|---|---|
| `ix_permissions_code` | `CREATE UNIQUE INDEX ix_permissions_code ON public.permissions USING btree (code)` |
| `pk_permissions` | `CREATE UNIQUE INDEX pk_permissions ON public.permissions USING btree (id)` |

## `products`

### Columns

| # | Column | Type | Null | Default |
|---:|---|---|:---:|---|
| 1 | `id` | `uuid` | NO | `` |
| 2 | `name` | `character varying(200)` | NO | `` |
| 3 | `category` | `character varying(100)` | NO | `` |
| 4 | `price` | `numeric(10,2)` | NO | `` |
| 5 | `status` | `character varying(20)` | NO | `'ACTIVE'::character varying` |
| 6 | `created_at` | `timestamp with time zone` | NO | `now()` |
| 7 | `updated_at` | `timestamp with time zone` | NO | `now()` |
| 8 | `sku` | `character varying(64)` | YES | `` |
| 9 | `description` | `text` | YES | `` |
| 10 | `image_url` | `character varying(1024)` | YES | `` |
| 11 | `source_product_id` | `character varying(100)` | YES | `` |
| 12 | `product_code` | `character varying(64)` | YES | `` |
| 13 | `source_category_code` | `character varying(100)` | YES | `` |
| 14 | `list_price` | `numeric(10,2)` | YES | `` |
| 15 | `currency` | `character varying(3)` | NO | `'VND'::character varying` |
| 16 | `weight_g` | `numeric(12,3)` | YES | `` |
| 17 | `length_cm` | `numeric(10,3)` | YES | `` |
| 18 | `height_cm` | `numeric(10,3)` | YES | `` |
| 19 | `width_cm` | `numeric(10,3)` | YES | `` |
| 20 | `photo_count` | `integer` | YES | `` |
| 21 | `is_deleted` | `boolean` | NO | `false` |

### Constraints

| Name | Type | Definition |
|---|---|---|
| `pk_products` | PRIMARY KEY | `PRIMARY KEY (id)` |

### Indexes

| Name | Definition |
|---|---|
| `ix_products_category` | `CREATE INDEX ix_products_category ON public.products USING btree (category)` |
| `ix_products_product_code` | `CREATE UNIQUE INDEX ix_products_product_code ON public.products USING btree (product_code)` |
| `ix_products_source_category_code` | `CREATE INDEX ix_products_source_category_code ON public.products USING btree (source_category_code)` |
| `ix_products_source_product_id` | `CREATE UNIQUE INDEX ix_products_source_product_id ON public.products USING btree (source_product_id)` |
| `pk_products` | `CREATE UNIQUE INDEX pk_products ON public.products USING btree (id)` |
| `uq_products_sku` | `CREATE UNIQUE INDEX uq_products_sku ON public.products USING btree (sku)` |

## `purchase_predictions`

### Columns

| # | Column | Type | Null | Default |
|---:|---|---|:---:|---|
| 1 | `id` | `uuid` | NO | `` |
| 2 | `customer_id` | `uuid` | NO | `` |
| 3 | `prediction_date` | `timestamp with time zone` | NO | `` |
| 4 | `prediction_horizon_days` | `integer` | NO | `` |
| 5 | `feature_window_days` | `integer` | NO | `` |
| 6 | `purchase_probability` | `numeric(6,4)` | NO | `` |
| 7 | `model_version` | `character varying(50)` | NO | `` |
| 8 | `features` | `json` | YES | `` |
| 9 | `created_at` | `timestamp with time zone` | NO | `now()` |
| 10 | `updated_at` | `timestamp with time zone` | NO | `now()` |
| 11 | `analysis_run_id` | `uuid` | YES | `` |
| 12 | `model_version_id` | `uuid` | YES | `` |
| 13 | `feature_from` | `timestamp with time zone` | YES | `` |
| 14 | `feature_to` | `timestamp with time zone` | YES | `` |

### Constraints

| Name | Type | Definition |
|---|---|---|
| `fk_purchase_predictions_analysis_run_id_analysis_runs` | FOREIGN KEY | `FOREIGN KEY (analysis_run_id) REFERENCES analysis_runs(id) ON DELETE SET NULL` |
| `fk_purchase_predictions_customer_id_customers` | FOREIGN KEY | `FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE` |
| `fk_purchase_predictions_model_version_id_model_registry` | FOREIGN KEY | `FOREIGN KEY (model_version_id) REFERENCES model_registry(id) ON DELETE SET NULL` |
| `pk_purchase_predictions` | PRIMARY KEY | `PRIMARY KEY (id)` |

### Indexes

| Name | Definition |
|---|---|
| `ix_purchase_predictions_analysis_run_id` | `CREATE INDEX ix_purchase_predictions_analysis_run_id ON public.purchase_predictions USING btree (analysis_run_id)` |
| `ix_purchase_predictions_customer_id` | `CREATE INDEX ix_purchase_predictions_customer_id ON public.purchase_predictions USING btree (customer_id)` |
| `ix_purchase_predictions_model_version_id` | `CREATE INDEX ix_purchase_predictions_model_version_id ON public.purchase_predictions USING btree (model_version_id)` |
| `pk_purchase_predictions` | `CREATE UNIQUE INDEX pk_purchase_predictions ON public.purchase_predictions USING btree (id)` |

## `refresh_tokens`

### Columns

| # | Column | Type | Null | Default |
|---:|---|---|:---:|---|
| 1 | `id` | `uuid` | NO | `` |
| 2 | `token_hash` | `character varying(64)` | NO | `` |
| 3 | `user_id` | `uuid` | NO | `` |
| 4 | `family_id` | `character varying(36)` | NO | `` |
| 5 | `revoked_at` | `timestamp with time zone` | YES | `` |
| 6 | `expires_at` | `timestamp with time zone` | NO | `` |
| 7 | `created_ip` | `character varying(45)` | YES | `` |
| 8 | `user_agent` | `character varying(500)` | YES | `` |
| 9 | `created_at` | `timestamp with time zone` | NO | `now()` |
| 10 | `updated_at` | `timestamp with time zone` | NO | `now()` |

### Constraints

| Name | Type | Definition |
|---|---|---|
| `fk_refresh_tokens_user_id_users` | FOREIGN KEY | `FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE` |
| `pk_refresh_tokens` | PRIMARY KEY | `PRIMARY KEY (id)` |

### Indexes

| Name | Definition |
|---|---|
| `ix_refresh_tokens_family_id` | `CREATE INDEX ix_refresh_tokens_family_id ON public.refresh_tokens USING btree (family_id)` |
| `ix_refresh_tokens_token_hash` | `CREATE UNIQUE INDEX ix_refresh_tokens_token_hash ON public.refresh_tokens USING btree (token_hash)` |
| `ix_refresh_tokens_user_family` | `CREATE INDEX ix_refresh_tokens_user_family ON public.refresh_tokens USING btree (user_id, family_id)` |
| `ix_refresh_tokens_user_id` | `CREATE INDEX ix_refresh_tokens_user_id ON public.refresh_tokens USING btree (user_id)` |
| `pk_refresh_tokens` | `CREATE UNIQUE INDEX pk_refresh_tokens ON public.refresh_tokens USING btree (id)` |

## `reviews`

### Columns

| # | Column | Type | Null | Default |
|---:|---|---|:---:|---|
| 1 | `id` | `uuid` | NO | `` |
| 2 | `created_at` | `timestamp with time zone` | NO | `now()` |
| 3 | `updated_at` | `timestamp with time zone` | NO | `now()` |
| 4 | `review_code` | `character varying(50)` | YES | `` |
| 5 | `order_id` | `uuid` | NO | `` |
| 6 | `customer_id` | `uuid` | NO | `` |
| 7 | `score` | `integer` | NO | `` |
| 8 | `title` | `character varying(255)` | YES | `` |
| 9 | `message` | `text` | YES | `` |
| 10 | `channel` | `character varying(50)` | YES | `` |
| 11 | `review_created_at` | `timestamp with time zone` | YES | `` |
| 12 | `answered_at` | `timestamp with time zone` | YES | `` |

### Constraints

| Name | Type | Definition |
|---|---|---|
| `ck_reviews_ck_reviews_score_range` | CHECK | `CHECK (((score >= 1) AND (score <= 5)))` |
| `fk_reviews_customer_id_customers` | FOREIGN KEY | `FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE` |
| `fk_reviews_order_id_orders` | FOREIGN KEY | `FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE` |
| `pk_reviews` | PRIMARY KEY | `PRIMARY KEY (id)` |
| `uq_reviews_review_code` | UNIQUE | `UNIQUE (review_code)` |

### Indexes

| Name | Definition |
|---|---|
| `ix_reviews_customer_id` | `CREATE INDEX ix_reviews_customer_id ON public.reviews USING btree (customer_id)` |
| `ix_reviews_order_id` | `CREATE INDEX ix_reviews_order_id ON public.reviews USING btree (order_id)` |
| `pk_reviews` | `CREATE UNIQUE INDEX pk_reviews ON public.reviews USING btree (id)` |
| `uq_reviews_review_code` | `CREATE UNIQUE INDEX uq_reviews_review_code ON public.reviews USING btree (review_code)` |

## `role_permissions`

### Columns

| # | Column | Type | Null | Default |
|---:|---|---|:---:|---|
| 1 | `role_id` | `uuid` | NO | `` |
| 2 | `permission_id` | `uuid` | NO | `` |

### Constraints

| Name | Type | Definition |
|---|---|---|
| `fk_role_permissions_permission_id_permissions` | FOREIGN KEY | `FOREIGN KEY (permission_id) REFERENCES permissions(id) ON DELETE CASCADE` |
| `fk_role_permissions_role_id_roles` | FOREIGN KEY | `FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE` |
| `pk_role_permissions` | PRIMARY KEY | `PRIMARY KEY (role_id, permission_id)` |

### Indexes

| Name | Definition |
|---|---|
| `pk_role_permissions` | `CREATE UNIQUE INDEX pk_role_permissions ON public.role_permissions USING btree (role_id, permission_id)` |

## `roles`

### Columns

| # | Column | Type | Null | Default |
|---:|---|---|:---:|---|
| 1 | `code` | `character varying(50)` | NO | `` |
| 2 | `name` | `character varying(100)` | NO | `` |
| 3 | `description` | `character varying(255)` | YES | `` |
| 4 | `id` | `uuid` | NO | `` |

### Constraints

| Name | Type | Definition |
|---|---|---|
| `pk_roles` | PRIMARY KEY | `PRIMARY KEY (id)` |

### Indexes

| Name | Definition |
|---|---|
| `ix_roles_code` | `CREATE UNIQUE INDEX ix_roles_code ON public.roles USING btree (code)` |
| `pk_roles` | `CREATE UNIQUE INDEX pk_roles ON public.roles USING btree (id)` |

## `scoring_rules`

### Columns

| # | Column | Type | Null | Default |
|---:|---|---|:---:|---|
| 1 | `id` | `uuid` | NO | `` |
| 2 | `configuration_version_id` | `uuid` | NO | `` |
| 3 | `component` | `character varying(50)` | NO | `` |
| 4 | `weight` | `numeric(6,4)` | NO | `` |
| 5 | `enabled` | `boolean` | NO | `true` |

### Constraints

| Name | Type | Definition |
|---|---|---|
| `fk_scoring_rules_configuration_version_id_configuration_c7a4` | FOREIGN KEY | `FOREIGN KEY (configuration_version_id) REFERENCES configuration_versions(id) ON DELETE CASCADE` |
| `pk_scoring_rules` | PRIMARY KEY | `PRIMARY KEY (id)` |
| `uq_scoring_rules_version_component` | UNIQUE | `UNIQUE (configuration_version_id, component)` |

### Indexes

| Name | Definition |
|---|---|
| `pk_scoring_rules` | `CREATE UNIQUE INDEX pk_scoring_rules ON public.scoring_rules USING btree (id)` |
| `uq_scoring_rules_version_component` | `CREATE UNIQUE INDEX uq_scoring_rules_version_component ON public.scoring_rules USING btree (configuration_version_id, component)` |

## `scoring_thresholds`

### Columns

| # | Column | Type | Null | Default |
|---:|---|---|:---:|---|
| 1 | `id` | `uuid` | NO | `` |
| 2 | `configuration_version_id` | `uuid` | NO | `` |
| 3 | `component` | `character varying(50)` | NO | `` |
| 4 | `min_value` | `numeric(12,4)` | YES | `` |
| 5 | `max_value` | `numeric(12,4)` | YES | `` |
| 6 | `score` | `numeric(6,2)` | NO | `` |
| 7 | `priority` | `integer` | NO | `0` |

### Constraints

| Name | Type | Definition |
|---|---|---|
| `fk_scoring_thresholds_configuration_version_id_configur_e953` | FOREIGN KEY | `FOREIGN KEY (configuration_version_id) REFERENCES configuration_versions(id) ON DELETE CASCADE` |
| `pk_scoring_thresholds` | PRIMARY KEY | `PRIMARY KEY (id)` |

### Indexes

| Name | Definition |
|---|---|
| `pk_scoring_thresholds` | `CREATE UNIQUE INDEX pk_scoring_thresholds ON public.scoring_thresholds USING btree (id)` |

## `segment_history`

### Columns

| # | Column | Type | Null | Default |
|---:|---|---|:---:|---|
| 1 | `id` | `uuid` | NO | `` |
| 2 | `customer_id` | `uuid` | NO | `` |
| 3 | `segment_type` | `character varying(50)` | NO | `` |
| 4 | `reason` | `character varying(500)` | NO | `` |
| 5 | `calculated_at` | `timestamp with time zone` | NO | `` |
| 6 | `created_at` | `timestamp with time zone` | NO | `now()` |
| 7 | `updated_at` | `timestamp with time zone` | NO | `now()` |
| 8 | `analysis_run_id` | `uuid` | YES | `` |
| 9 | `segment_code` | `character varying(50)` | YES | `` |
| 10 | `segment_name` | `character varying(100)` | YES | `` |
| 11 | `configuration_version_id` | `uuid` | YES | `` |

### Constraints

| Name | Type | Definition |
|---|---|---|
| `fk_segment_history_analysis_run_id_analysis_runs` | FOREIGN KEY | `FOREIGN KEY (analysis_run_id) REFERENCES analysis_runs(id) ON DELETE CASCADE` |
| `fk_segment_history_config_version_id` | FOREIGN KEY | `FOREIGN KEY (configuration_version_id) REFERENCES configuration_versions(id) ON DELETE SET NULL` |
| `fk_segment_history_customer_id_customers` | FOREIGN KEY | `FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE` |
| `pk_segment_history` | PRIMARY KEY | `PRIMARY KEY (id)` |

### Indexes

| Name | Definition |
|---|---|
| `ix_segment_history_analysis_run_id` | `CREATE INDEX ix_segment_history_analysis_run_id ON public.segment_history USING btree (analysis_run_id)` |
| `ix_segment_history_configuration_version_id` | `CREATE INDEX ix_segment_history_configuration_version_id ON public.segment_history USING btree (configuration_version_id)` |
| `ix_segment_history_customer_id` | `CREATE INDEX ix_segment_history_customer_id ON public.segment_history USING btree (customer_id)` |
| `ix_segment_history_segment_type` | `CREATE INDEX ix_segment_history_segment_type ON public.segment_history USING btree (segment_type)` |
| `pk_segment_history` | `CREATE UNIQUE INDEX pk_segment_history ON public.segment_history USING btree (id)` |

## `segmentation_rules`

### Columns

| # | Column | Type | Null | Default |
|---:|---|---|:---:|---|
| 1 | `id` | `uuid` | NO | `` |
| 2 | `configuration_version_id` | `uuid` | NO | `` |
| 3 | `segment_code` | `character varying(50)` | NO | `` |
| 4 | `min_potential_score` | `numeric(6,2)` | YES | `` |
| 5 | `max_potential_score` | `numeric(6,2)` | YES | `` |
| 6 | `priority` | `integer` | NO | `0` |
| 7 | `enabled` | `boolean` | NO | `true` |

### Constraints

| Name | Type | Definition |
|---|---|---|
| `fk_segmentation_rules_configuration_version_id_configur_3a9a` | FOREIGN KEY | `FOREIGN KEY (configuration_version_id) REFERENCES configuration_versions(id) ON DELETE CASCADE` |
| `pk_segmentation_rules` | PRIMARY KEY | `PRIMARY KEY (id)` |

### Indexes

| Name | Definition |
|---|---|
| `pk_segmentation_rules` | `CREATE UNIQUE INDEX pk_segmentation_rules ON public.segmentation_rules USING btree (id)` |

## `sellers`

### Columns

| # | Column | Type | Null | Default |
|---:|---|---|:---:|---|
| 1 | `id` | `uuid` | NO | `` |
| 2 | `created_at` | `timestamp with time zone` | NO | `now()` |
| 3 | `updated_at` | `timestamp with time zone` | NO | `now()` |
| 4 | `seller_code` | `character varying(50)` | NO | `` |
| 5 | `seller_name` | `character varying(150)` | YES | `` |
| 6 | `zip_code` | `character varying(20)` | YES | `` |
| 7 | `city` | `character varying(100)` | YES | `` |
| 8 | `state_code` | `character varying(20)` | YES | `` |
| 9 | `region` | `character varying(100)` | YES | `` |

### Constraints

| Name | Type | Definition |
|---|---|---|
| `pk_sellers` | PRIMARY KEY | `PRIMARY KEY (id)` |
| `uq_sellers_seller_code` | UNIQUE | `UNIQUE (seller_code)` |

### Indexes

| Name | Definition |
|---|---|
| `pk_sellers` | `CREATE UNIQUE INDEX pk_sellers ON public.sellers USING btree (id)` |
| `uq_sellers_seller_code` | `CREATE UNIQUE INDEX uq_sellers_seller_code ON public.sellers USING btree (seller_code)` |

## `teams`

### Columns

| # | Column | Type | Null | Default |
|---:|---|---|:---:|---|
| 1 | `id` | `uuid` | NO | `` |
| 2 | `created_at` | `timestamp with time zone` | NO | `now()` |
| 3 | `updated_at` | `timestamp with time zone` | NO | `now()` |
| 4 | `code` | `character varying(50)` | NO | `` |
| 5 | `name` | `character varying(100)` | NO | `` |
| 6 | `description` | `character varying(255)` | YES | `` |
| 7 | `is_active` | `boolean` | NO | `true` |

### Constraints

| Name | Type | Definition |
|---|---|---|
| `pk_teams` | PRIMARY KEY | `PRIMARY KEY (id)` |

### Indexes

| Name | Definition |
|---|---|
| `ix_teams_code` | `CREATE UNIQUE INDEX ix_teams_code ON public.teams USING btree (code)` |
| `pk_teams` | `CREATE UNIQUE INDEX pk_teams ON public.teams USING btree (id)` |

## `users`

### Columns

| # | Column | Type | Null | Default |
|---:|---|---|:---:|---|
| 1 | `email` | `character varying(255)` | NO | `` |
| 2 | `password_hash` | `character varying(255)` | NO | `` |
| 3 | `full_name` | `character varying(100)` | NO | `` |
| 4 | `status` | `userstatus` | NO | `'ACTIVE'::userstatus` |
| 5 | `role_id` | `uuid` | NO | `` |
| 6 | `failed_login_count` | `integer` | NO | `` |
| 7 | `locked_until` | `timestamp with time zone` | YES | `` |
| 8 | `last_login_at` | `timestamp with time zone` | YES | `` |
| 9 | `id` | `uuid` | NO | `` |
| 10 | `created_at` | `timestamp with time zone` | NO | `now()` |
| 11 | `updated_at` | `timestamp with time zone` | NO | `now()` |
| 12 | `google_id` | `character varying(100)` | YES | `` |
| 13 | `auth_provider` | `character varying(20)` | NO | `` |
| 14 | `team_id` | `uuid` | YES | `` |
| 15 | `employee_id` | `uuid` | YES | `` |

### Constraints

| Name | Type | Definition |
|---|---|---|
| `fk_users_employee_id_employees` | FOREIGN KEY | `FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE SET NULL` |
| `fk_users_role_id_roles` | FOREIGN KEY | `FOREIGN KEY (role_id) REFERENCES roles(id)` |
| `fk_users_team_id_teams` | FOREIGN KEY | `FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE SET NULL` |
| `pk_users` | PRIMARY KEY | `PRIMARY KEY (id)` |

### Indexes

| Name | Definition |
|---|---|
| `ix_users_email` | `CREATE UNIQUE INDEX ix_users_email ON public.users USING btree (email)` |
| `ix_users_employee_id` | `CREATE INDEX ix_users_employee_id ON public.users USING btree (employee_id)` |
| `ix_users_google_id` | `CREATE UNIQUE INDEX ix_users_google_id ON public.users USING btree (google_id)` |
| `ix_users_team_id` | `CREATE INDEX ix_users_team_id ON public.users USING btree (team_id)` |
| `pk_users` | `CREATE UNIQUE INDEX pk_users ON public.users USING btree (id)` |

## `valid_order_status_configs`

### Columns

| # | Column | Type | Null | Default |
|---:|---|---|:---:|---|
| 1 | `id` | `uuid` | NO | `` |
| 2 | `configuration_version_id` | `uuid` | NO | `` |
| 3 | `order_status` | `character varying(30)` | NO | `` |
| 4 | `is_valid_for_analytics` | `boolean` | NO | `` |

### Constraints

| Name | Type | Definition |
|---|---|---|
| `fk_valid_order_status_configs_configuration_version_id__7c12` | FOREIGN KEY | `FOREIGN KEY (configuration_version_id) REFERENCES configuration_versions(id) ON DELETE CASCADE` |
| `pk_valid_order_status_configs` | PRIMARY KEY | `PRIMARY KEY (id)` |
| `uq_valid_order_status_config_version_status` | UNIQUE | `UNIQUE (configuration_version_id, order_status)` |

### Indexes

| Name | Definition |
|---|---|
| `pk_valid_order_status_configs` | `CREATE UNIQUE INDEX pk_valid_order_status_configs ON public.valid_order_status_configs USING btree (id)` |
| `uq_valid_order_status_config_version_status` | `CREATE UNIQUE INDEX uq_valid_order_status_config_version_status ON public.valid_order_status_configs USING btree (configuration_version_id, order_status)` |

## PostgreSQL enum types

| Type | Values |
|---|---|
| `userstatus` | ACTIVE, DISABLED, LOCKED |
