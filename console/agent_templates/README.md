# Agent Templates — Master Index

Catalog of **46 agent cards** — 40 pipeline templates (phases 0-5, one per skill in the project-analysis pipeline) plus 6 standalone financial-market templates.

Every card carries YAML frontmatter (see [`_schema.md`](_schema.md)) so the Agent Factory can query, filter and auto-order runs from a single field set. Add a new card: drop a `.md` file under the matching category folder, populate the frontmatter, then rerun `scripts/build_agent_templates_index.py` to refresh this page.

## Contents

- [Overview by category](#overview-by-category)
  - [Phase 0 · Intake](#phase-0--intake)
  - [Phase 1 · Market research](#phase-1--market-research)
  - [Phase 2 · Minimal viable setup](#phase-2--minimal-viable-setup)
  - [Phase 3 · Market validation](#phase-3--market-validation)
  - [Phase 4 · Post-gate scaling](#phase-4--post-gate-scaling)
  - [Phase 5 · Investor deliverable](#phase-5--investor-deliverable)
  - [Standalone · Financial markets (TradingAgents / OpenBB inspired)](#standalone--financial-markets-tradingagents--openbb-inspired)
- [Gates](#gates)
- [Optional templates](#optional-templates)
- [Index by role](#index-by-role)
- [Index by tag](#index-by-tag)

## Overview by category

| Category | Templates | Phase |
| --- | ---: | --- |
| [Phase 0 · Intake](#phase-0--intake) | 1 | Phase 0 |
| [Phase 1 · Market research](#phase-1--market-research) | 10 | Phase 1 |
| [Phase 2 · Minimal viable setup](#phase-2--minimal-viable-setup) | 5 | Phase 2 |
| [Phase 3 · Market validation](#phase-3--market-validation) | 6 | Phase 3 |
| [Phase 4 · Post-gate scaling](#phase-4--post-gate-scaling) | 17 | Phase 4 |
| [Phase 5 · Investor deliverable](#phase-5--investor-deliverable) | 1 | Phase 5 |
| [Standalone · Financial markets (TradingAgents / OpenBB inspired)](#standalone--financial-markets-tradingagents--openbb-inspired) | 6 | — |

## Phase 0 · Intake

| Step | Id | Role | Mode | Produces | Flags |
| ---: | --- | --- | --- | --- | --- |
| 0 | [`project_intake_facilitator`](intake/project_intake_facilitator.md) | writer | single-shot | questionnaire |  |

## Phase 1 · Market research

| Step | Id | Role | Mode | Produces | Flags |
| ---: | --- | --- | --- | --- | --- |
| 1 | [`market_problem_analyst`](market-research/market_problem_analyst.md) | analyst | pipeline-stage | markdown_report |  |
| 2 | [`market_customer_profiler`](market-research/market_customer_profiler.md) | analyst | pipeline-stage | markdown_report |  |
| 3 | [`market_study_by_country_analyst`](market-research/market_study_by_country_analyst.md) | analyst | pipeline-stage | markdown_report |  |
| 4 | [`market_trends_timing_analyst`](market-research/market_trends_timing_analyst.md) | analyst | pipeline-stage | markdown_report |  |
| 5 | [`competitive_analyst`](market-research/competitive_analyst.md) | analyst | pipeline-stage | markdown_report |  |
| 6 | [`swot_analyst`](market-research/swot_analyst.md) | analyst | pipeline-stage | markdown_report |  |
| 7 | [`brand_identity_writer`](market-research/brand_identity_writer.md) | writer | pipeline-stage | markdown_report |  |
| 8 | [`pricing_strategist`](market-research/pricing_strategist.md) | analyst | pipeline-stage | markdown_report |  |
| 9 | [`market_gap_analyst`](market-research/market_gap_analyst.md) | analyst | pipeline-stage | markdown_report |  |
| 10 | [`strategic_decision_gate`](market-research/strategic_decision_gate.md) | judge | gate | decision | **gate** |

## Phase 2 · Minimal viable setup

| Step | Id | Role | Mode | Produces | Flags |
| ---: | --- | --- | --- | --- | --- |
| 11 | [`resource_inventory_analyst`](mvs/resource_inventory_analyst.md) | analyst | pipeline-stage | markdown_report |  |
| 12 | [`legal_setup_cost_estimator`](mvs/legal_setup_cost_estimator.md) | analyst | pipeline-stage | markdown_report |  |
| 13 | [`mvp_scoper`](mvs/mvp_scoper.md) | analyst | pipeline-stage | markdown_report |  |
| 14 | [`minimal_tech_stack_cost_estimator`](mvs/minimal_tech_stack_cost_estimator.md) | analyst | pipeline-stage | markdown_report |  |
| 15 | [`tranche_0_budgeter`](mvs/tranche_0_budgeter.md) | integrator | pipeline-stage | markdown_report |  |

## Phase 3 · Market validation

| Step | Id | Role | Mode | Produces | Flags |
| ---: | --- | --- | --- | --- | --- |
| 16 | [`validation_hypotheses_analyst`](validation/validation_hypotheses_analyst.md) | analyst | pipeline-stage | markdown_report |  |
| 17 | [`channel_economics_modeler`](validation/channel_economics_modeler.md) | analyst | pipeline-stage | markdown_report |  |
| 18 | [`ltv_cac_targeter`](validation/ltv_cac_targeter.md) | analyst | pipeline-stage | markdown_report |  |
| 19 | [`validation_experiment_designer`](validation/validation_experiment_designer.md) | analyst | pipeline-stage | markdown_report |  |
| 20 | [`tranche_1_budgeter`](validation/tranche_1_budgeter.md) | integrator | pipeline-stage | markdown_report |  |
| 21 | [`scaling_gate_definer`](validation/scaling_gate_definer.md) | judge | gate | decision | **gate** |

## Phase 4 · Post-gate scaling

| Step | Id | Role | Mode | Produces | Flags |
| ---: | --- | --- | --- | --- | --- |
| 22 | [`kpis_okrs_framework_writer`](scaling/kpis_okrs_framework_writer.md) | writer | pipeline-stage | markdown_report |  |
| 23 | [`product_roadmap_writer`](scaling/product_roadmap_writer.md) | writer | pipeline-stage | markdown_report |  |
| 24 | [`functional_specifier`](scaling/functional_specifier.md) | writer | pipeline-stage | markdown_report |  |
| 25 | [`user_roles_permissions_writer`](scaling/user_roles_permissions_writer.md) | writer | pipeline-stage | markdown_report |  |
| 26 | [`platform_areas_architect`](scaling/platform_areas_architect.md) | analyst | pipeline-stage | markdown_report |  |
| 27 | [`mobile_app_specifier`](scaling/mobile_app_specifier.md) | writer | pipeline-stage | markdown_report | _optional_ |
| 28 | [`data_schema_designer`](scaling/data_schema_designer.md) | analyst | pipeline-stage | markdown_report |  |
| 29 | [`ux_platform_designer`](scaling/ux_platform_designer.md) | writer | pipeline-stage | markdown_report |  |
| 30 | [`gtm_strategist`](scaling/gtm_strategist.md) | writer | pipeline-stage | markdown_report |  |
| 31 | [`tech_stack_vendors_analyst`](scaling/tech_stack_vendors_analyst.md) | analyst | pipeline-stage | markdown_report |  |
| 32 | [`legal_ip_analyst`](scaling/legal_ip_analyst.md) | analyst | pipeline-stage | markdown_report |  |
| 33 | [`risk_assessor`](scaling/risk_assessor.md) | analyst | pipeline-stage | markdown_report |  |
| 34 | [`financial_business_planner`](scaling/financial_business_planner.md) | writer | pipeline-stage | markdown_report |  |
| 35 | [`financial_excel_builder`](scaling/financial_excel_builder.md) | analyst | pipeline-stage | xlsx |  |
| 36 | [`startup_valuation_analyst`](scaling/startup_valuation_analyst.md) | analyst | pipeline-stage | markdown_report | _optional_ |
| 37 | [`fundraising_strategist`](scaling/fundraising_strategist.md) | writer | pipeline-stage | markdown_report | _optional_ |
| 38 | [`executive_summary_writer`](scaling/executive_summary_writer.md) | writer | pipeline-stage | pdf |  |

## Phase 5 · Investor deliverable

| Step | Id | Role | Mode | Produces | Flags |
| ---: | --- | --- | --- | --- | --- |
| 39 | [`pitch_deck_designer`](investor-deliverable/pitch_deck_designer.md) | writer | pipeline-stage | pptx |  |

## Standalone · Financial markets (TradingAgents / OpenBB inspired)

| Step | Id | Role | Mode | Produces | Flags |
| ---: | --- | --- | --- | --- | --- |
| — | [`bull_bear_debate_pair`](finance/bull_bear_debate_pair.md) | debater | debate | structured_json |  |
| — | [`fundamental_analyst`](finance/fundamental_analyst.md) | analyst | single-shot | structured_json |  |
| — | [`macro_context_agent`](finance/macro_context_agent.md) | analyst | single-shot | structured_json |  |
| — | [`market_research_analyst`](finance/market_research_analyst.md) | analyst | single-shot | structured_json |  |
| — | [`memory_reflector`](finance/memory_reflector.md) | reflector | reflector | reflection |  |
| — | [`risk_committee`](finance/risk_committee.md) | debater | debate | structured_json |  |

## Gates

Templates that emit a binary or thresholded decision. Downstream templates must refuse to run until the upstream gate returns PASS.

| Step | Id | Category |
| ---: | --- | --- |
| 10 | [`strategic_decision_gate`](market-research/strategic_decision_gate.md) | market-research |
| 21 | [`scaling_gate_definer`](validation/scaling_gate_definer.md) | validation |

## Optional templates

Templates the coordinator skips unless upstream logic activates them (e.g. mobile-app spec only if step 26 recommends mobile, valuation and fundraising only if the founder chooses to raise).

| Step | Id | Category |
| ---: | --- | --- |
| 27 | [`mobile_app_specifier`](scaling/mobile_app_specifier.md) | scaling |
| 36 | [`startup_valuation_analyst`](scaling/startup_valuation_analyst.md) | scaling |
| 37 | [`fundraising_strategist`](scaling/fundraising_strategist.md) | scaling |

## Index by role

| Role | Count | Templates |
| --- | ---: | --- |
| `analyst` | 26 | `channel_economics_modeler`, `competitive_analyst`, `data_schema_designer`, `financial_excel_builder`, `fundamental_analyst`, `legal_ip_analyst`, `legal_setup_cost_estimator`, `ltv_cac_targeter`, `macro_context_agent`, `market_customer_profiler`, `market_gap_analyst`, `market_problem_analyst`, `market_research_analyst`, `market_study_by_country_analyst`, `market_trends_timing_analyst`, `minimal_tech_stack_cost_estimator`, `mvp_scoper`, `platform_areas_architect`, `pricing_strategist`, `resource_inventory_analyst`, `risk_assessor`, `startup_valuation_analyst`, `swot_analyst`, `tech_stack_vendors_analyst`, `validation_experiment_designer`, `validation_hypotheses_analyst` |
| `debater` | 2 | `bull_bear_debate_pair`, `risk_committee` |
| `integrator` | 2 | `tranche_0_budgeter`, `tranche_1_budgeter` |
| `judge` | 2 | `scaling_gate_definer`, `strategic_decision_gate` |
| `reflector` | 1 | `memory_reflector` |
| `writer` | 13 | `brand_identity_writer`, `executive_summary_writer`, `financial_business_planner`, `functional_specifier`, `fundraising_strategist`, `gtm_strategist`, `kpis_okrs_framework_writer`, `mobile_app_specifier`, `pitch_deck_designer`, `product_roadmap_writer`, `project_intake_facilitator`, `user_roles_permissions_writer`, `ux_platform_designer` |

## Index by tag

| Tag | Templates |
| --- | --- |
| `acceptance` | `functional_specifier` |
| `adoption` | `market_trends_timing_analyst` |
| `alive-cost` | `minimal_tech_stack_cost_estimator` |
| `android` | `mobile_app_specifier` |
| `architecture` | `platform_areas_architect` |
| `areas` | `platform_areas_architect` |
| `bear` | `bull_bear_debate_pair` |
| `benchmarks` | `channel_economics_modeler` |
| `berkus` | `startup_valuation_analyst` |
| `blue-ocean` | `market_gap_analyst` |
| `brand` | `brand_identity_writer` |
| `budget` | `tranche_0_budgeter`, `tranche_1_budgeter` |
| `build-vs-buy` | `tech_stack_vendors_analyst` |
| `bull` | `bull_bear_debate_pair` |
| `business-plan` | `financial_business_planner` |
| `cac` | `channel_economics_modeler`, `ltv_cac_targeter` |
| `cac-ltv` | `scaling_gate_definer` |
| `calendar` | `tranche_1_budgeter` |
| `cap-table` | `resource_inventory_analyst` |
| `capital` | `tranche_0_budgeter`, `tranche_1_budgeter` |
| `cash-flow` | `tranche_0_budgeter` |
| `channels` | `channel_economics_modeler` |
| `chart` | `market_research_analyst` |
| `checkpoint` | `scaling_gate_definer`, `strategic_decision_gate` |
| `cloud` | `tech_stack_vendors_analyst` |
| `committee` | `risk_committee` |
| `comparables` | `startup_valuation_analyst` |
| `competition` | `competitive_analyst` |
| `content` | `validation_experiment_designer` |
| `country` | `market_study_by_country_analyst` |
| `cpc` | `channel_economics_modeler` |
| `cpl` | `channel_economics_modeler` |
| `cpm` | `channel_economics_modeler` |
| `customer` | `market_customer_profiler` |
| `dafo` | `swot_analyst` |
| `data-model` | `data_schema_designer` |
| `dcf` | `startup_valuation_analyst` |
| `debate` | `bull_bear_debate_pair` |
| `dependencies` | `risk_assessor` |
| `docx` | `project_intake_facilitator` |
| `dpa` | `legal_ip_analyst` |
| `elasticity` | `pricing_strategist` |
| `entities` | `data_schema_designer` |
| `equity` | `fundamental_analyst`, `market_research_analyst` |
| `executive-summary` | `executive_summary_writer` |
| `experiments` | `validation_experiment_designer` |
| `features` | `competitive_analyst` |
| `filings` | `fundamental_analyst` |
| `finance` | `bull_bear_debate_pair`, `fundamental_analyst`, `macro_context_agent`, `market_research_analyst`, `memory_reflector`, `risk_committee` |
| `financials` | `financial_business_planner`, `financial_excel_builder` |
| `flows` | `data_schema_designer` |
| `founder-onboarding` | `project_intake_facilitator` |
| `fred` | `macro_context_agent` |
| `functional-spec` | `functional_specifier` |
| `fundamentals` | `fundamental_analyst` |
| `fundraising` | `fundraising_strategist` |
| `gap` | `market_gap_analyst` |
| `gate` | `strategic_decision_gate` |
| `gate-1` | `scaling_gate_definer` |
| `gdpr` | `legal_ip_analyst` |
| `geo` | `market_study_by_country_analyst` |
| `go-no-go` | `strategic_decision_gate` |
| `go-to-market` | `gtm_strategist` |
| `gtm` | `gtm_strategist` |
| `hiring` | `financial_business_planner` |
| `hypothesis` | `validation_hypotheses_analyst` |
| `iam` | `user_roles_permissions_writer` |
| `identity` | `brand_identity_writer` |
| `in-scope` | `mvp_scoper` |
| `incorporation` | `legal_setup_cost_estimator` |
| `information-architecture` | `ux_platform_designer` |
| `intake` | `project_intake_facilitator` |
| `inventory` | `resource_inventory_analyst` |
| `investor` | `pitch_deck_designer` |
| `investors` | `fundraising_strategist` |
| `ios` | `mobile_app_specifier` |
| `ip` | `legal_ip_analyst` |
| `judge` | `bull_bear_debate_pair` |
| `kpi` | `kpis_okrs_framework_writer` |
| `landing` | `validation_experiment_designer` |
| `launch` | `gtm_strategist` |
| `legal` | `legal_ip_analyst`, `legal_setup_cost_estimator` |
| `logo` | `brand_identity_writer` |
| `ltv` | `ltv_cac_targeter` |
| `macro` | `macro_context_agent` |
| `market` | `competitive_analyst`, `market_customer_profiler`, `market_problem_analyst`, `market_study_by_country_analyst`, `market_trends_timing_analyst` |
| `matrix` | `risk_assessor` |
| `memory` | `memory_reflector` |
| `metrics` | `kpis_okrs_framework_writer` |
| `milestones` | `product_roadmap_writer` |
| `mitigation` | `risk_assessor` |
| `mobile` | `mobile_app_specifier` |
| `modules` | `platform_areas_architect` |
| `monetization` | `pricing_strategist` |
| `motion` | `gtm_strategist` |
| `mvp` | `minimal_tech_stack_cost_estimator`, `mvp_scoper` |
| `mvs` | `resource_inventory_analyst` |
| `naming` | `brand_identity_writer` |
| `navigation` | `ux_platform_designer` |
| `north-star` | `kpis_okrs_framework_writer` |
| `okr` | `kpis_okrs_framework_writer` |
| `one-pager` | `executive_summary_writer` |
| `openbb` | `fundamental_analyst`, `macro_context_agent`, `market_research_analyst` |
| `optional` | `fundraising_strategist`, `mobile_app_specifier`, `startup_valuation_analyst` |
| `out-of-scope` | `mvp_scoper` |
| `outbound` | `validation_experiment_designer` |
| `outcome` | `memory_reflector` |
| `pain-points` | `market_problem_analyst` |
| `pdf` | `executive_summary_writer` |
| `permissions` | `user_roles_permissions_writer` |
| `personas` | `market_customer_profiler` |
| `phase-1` | `brand_identity_writer`, `competitive_analyst`, `market_customer_profiler`, `market_gap_analyst`, `market_problem_analyst`, `market_study_by_country_analyst`, `market_trends_timing_analyst`, `pricing_strategist`, `strategic_decision_gate`, `swot_analyst` |
| `phase-2` | `legal_setup_cost_estimator`, `minimal_tech_stack_cost_estimator`, `mvp_scoper`, `resource_inventory_analyst`, `tranche_0_budgeter` |
| `phase-3` | `channel_economics_modeler`, `ltv_cac_targeter`, `scaling_gate_definer`, `tranche_1_budgeter`, `validation_experiment_designer`, `validation_hypotheses_analyst` |
| `phase-4` | `data_schema_designer`, `executive_summary_writer`, `financial_business_planner`, `financial_excel_builder`, `functional_specifier`, `fundraising_strategist`, `gtm_strategist`, `kpis_okrs_framework_writer`, `legal_ip_analyst`, `mobile_app_specifier`, `platform_areas_architect`, `product_roadmap_writer`, `risk_assessor`, `startup_valuation_analyst`, `tech_stack_vendors_analyst`, `user_roles_permissions_writer`, `ux_platform_designer` |
| `phase-5` | `pitch_deck_designer` |
| `phase-boundary` | `scaling_gate_definer`, `strategic_decision_gate`, `tranche_0_budgeter` |
| `pitch-deck` | `pitch_deck_designer` |
| `pivot` | `strategic_decision_gate` |
| `platform` | `platform_areas_architect` |
| `portfolio-manager` | `risk_committee` |
| `positioning` | `competitive_analyst` |
| `postmortem` | `memory_reflector` |
| `pptx` | `pitch_deck_designer` |
| `pricing` | `competitive_analyst`, `pricing_strategist` |
| `problem` | `market_problem_analyst` |
| `projections` | `financial_excel_builder` |
| `pwa` | `mobile_app_specifier` |
| `quadrant` | `market_gap_analyst` |
| `quarters` | `product_roadmap_writer` |
| `questionnaire` | `project_intake_facilitator` |
| `rates` | `macro_context_agent` |
| `rbac` | `user_roles_permissions_writer` |
| `reflection` | `memory_reflector` |
| `resources` | `resource_inventory_analyst` |
| `revenue-model` | `financial_business_planner` |
| `risk` | `risk_assessor`, `risk_committee` |
| `roadmap` | `product_roadmap_writer` |
| `roles` | `user_roles_permissions_writer` |
| `round` | `fundraising_strategist` |
| `sam` | `market_study_by_country_analyst` |
| `scaling` | `scaling_gate_definer` |
| `schema` | `data_schema_designer` |
| `scope` | `mvp_scoper` |
| `scorecard` | `startup_valuation_analyst` |
| `sec-edgar` | `fundamental_analyst` |
| `segment-channel-message` | `validation_hypotheses_analyst` |
| `segmentation` | `market_customer_profiler` |
| `sensitivity` | `financial_excel_builder` |
| `seo` | `validation_experiment_designer` |
| `sizing` | `risk_committee` |
| `som` | `market_study_by_country_analyst` |
| `states` | `ux_platform_designer` |
| `swot` | `swot_analyst` |
| `synthesis` | `swot_analyst` |
| `tam` | `market_study_by_country_analyst` |
| `tech-stack` | `minimal_tech_stack_cost_estimator`, `tech_stack_vendors_analyst` |
| `technical` | `market_research_analyst` |
| `term-sheet` | `fundraising_strategist` |
| `terms` | `legal_ip_analyst` |
| `thesis` | `bull_bear_debate_pair` |
| `threshold` | `ltv_cac_targeter` |
| `tiers` | `pricing_strategist` |
| `timing` | `market_trends_timing_analyst` |
| `tone` | `brand_identity_writer` |
| `trademark` | `legal_ip_analyst`, `legal_setup_cost_estimator` |
| `tramo-0` | `legal_setup_cost_estimator`, `minimal_tech_stack_cost_estimator`, `tranche_0_budgeter` |
| `tramo-1` | `tranche_1_budgeter` |
| `trends` | `market_trends_timing_analyst` |
| `unit-economics` | `ltv_cac_targeter` |
| `user-stories` | `functional_specifier` |
| `ux` | `ux_platform_designer` |
| `validation` | `validation_hypotheses_analyst` |
| `valuation` | `startup_valuation_analyst` |
| `vendors` | `tech_stack_vendors_analyst` |
| `white-space` | `market_gap_analyst` |
| `xlsx` | `financial_excel_builder` |
| `zero-cost` | `resource_inventory_analyst` |
