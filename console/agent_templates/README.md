# Agent Templates — Master Index

Catalogue of **229 cards** across two independent axes: **46 project-lifecycle cards** (phases 0-5 + standalone finance) and **183 business-operations cards** (7 domains × 4 rollout stages × 3 autonomy levels). By artefact: **161 agents · 52 sidecars · 16 skills**.

Every card carries YAML frontmatter (see [`_schema.md`](_schema.md)). Regenerate this index and the machine-readable [`catalog.json`](catalog.json) via `scripts/build_agent_templates_index.py`.

## Contents

- [Project lifecycle catalogue](#project-lifecycle-catalogue)
- [Business operations catalogue](#business-operations-catalogue)
- [Vertical adapters](#vertical-adapters)
- [Gates](#gates)
- [Optional templates](#optional-templates)
- [Index by role](#index-by-role)
- [Index by tag](#index-by-tag)

## Project lifecycle catalogue

Templates that run through the zero-to-fundraise arc (phases 0-5) plus standalone financial-market cards.

| Category | Templates | Phase |
| --- | ---: | --- |
| Phase 0 · Intake | 1 | Phase 0 |
| Phase 1 · Market research | 10 | Phase 1 |
| Phase 2 · Minimal viable setup | 5 | Phase 2 |
| Phase 3 · Market validation | 6 | Phase 3 |
| Phase 4 · Post-gate scaling | 17 | Phase 4 |
| Phase 5 · Investor deliverable | 1 | Phase 5 |
| Standalone · Financial markets (TradingAgents / OpenBB inspired) | 6 | — |

### Phase 0 · Intake

| Step | Id | Role | Mode | Produces | Flags |
| ---: | --- | --- | --- | --- | --- |
| 0 | [`project_intake_facilitator`](intake/project_intake_facilitator.md) | writer | single-shot | questionnaire |  |

### Phase 1 · Market research

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

### Phase 2 · Minimal viable setup

| Step | Id | Role | Mode | Produces | Flags |
| ---: | --- | --- | --- | --- | --- |
| 11 | [`resource_inventory_analyst`](mvs/resource_inventory_analyst.md) | analyst | pipeline-stage | markdown_report |  |
| 12 | [`legal_setup_cost_estimator`](mvs/legal_setup_cost_estimator.md) | analyst | pipeline-stage | markdown_report |  |
| 13 | [`mvp_scoper`](mvs/mvp_scoper.md) | analyst | pipeline-stage | markdown_report |  |
| 14 | [`minimal_tech_stack_cost_estimator`](mvs/minimal_tech_stack_cost_estimator.md) | analyst | pipeline-stage | markdown_report |  |
| 15 | [`tranche_0_budgeter`](mvs/tranche_0_budgeter.md) | integrator | pipeline-stage | markdown_report |  |

### Phase 3 · Market validation

| Step | Id | Role | Mode | Produces | Flags |
| ---: | --- | --- | --- | --- | --- |
| 16 | [`validation_hypotheses_analyst`](validation/validation_hypotheses_analyst.md) | analyst | pipeline-stage | markdown_report |  |
| 17 | [`channel_economics_modeler`](validation/channel_economics_modeler.md) | analyst | pipeline-stage | markdown_report |  |
| 18 | [`ltv_cac_targeter`](validation/ltv_cac_targeter.md) | analyst | pipeline-stage | markdown_report |  |
| 19 | [`validation_experiment_designer`](validation/validation_experiment_designer.md) | analyst | pipeline-stage | markdown_report |  |
| 20 | [`tranche_1_budgeter`](validation/tranche_1_budgeter.md) | integrator | pipeline-stage | markdown_report |  |
| 21 | [`scaling_gate_definer`](validation/scaling_gate_definer.md) | judge | gate | decision | **gate** |

### Phase 4 · Post-gate scaling

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

### Phase 5 · Investor deliverable

| Step | Id | Role | Mode | Produces | Flags |
| ---: | --- | --- | --- | --- | --- |
| 39 | [`pitch_deck_designer`](investor-deliverable/pitch_deck_designer.md) | writer | pipeline-stage | pptx |  |

### Standalone · Financial markets (TradingAgents / OpenBB inspired)

| Step | Id | Role | Mode | Produces | Flags |
| ---: | --- | --- | --- | --- | --- |
| — | [`bull_bear_debate_pair`](finance/bull_bear_debate_pair.md) | debater | debate | structured_json |  |
| — | [`fundamental_analyst`](finance/fundamental_analyst.md) | analyst | single-shot | structured_json |  |
| — | [`macro_context_agent`](finance/macro_context_agent.md) | analyst | single-shot | structured_json |  |
| — | [`market_research_analyst`](finance/market_research_analyst.md) | analyst | single-shot | structured_json |  |
| — | [`memory_reflector`](finance/memory_reflector.md) | reflector | reflector | reflection |  |
| — | [`risk_committee`](finance/risk_committee.md) | debater | debate | structured_json |  |

## Business operations catalogue

Templates that operate a running business — organised by domain, then plotted on a rollout matrix (rows = rollout stage, columns = autonomy). Icons: 🤖 agent · ⚙️ sidecar · 🧩 skill.

| Domain | Cards |
| --- | ---: |
| [Sales](#sales) | 33 |
| [Deals](#deals) | 28 |
| [Marketing](#marketing) | 24 |
| [Operations](#operations) | 37 |
| [Intelligence](#intelligence) | 23 |
| [Customer](#customer) | 16 |
| [Back Office](#back-office) | 22 |

### Sales

| Rollout \ Autonomy | human-led | human-assisted | fully-autonomous |
| --- | --- | --- | --- |
| 1-foundation |  | 🤖 [`lookalike_modeling`](sales/lookalike_modeling.md) | 🧩 [`account_enrichment`](skills/account_enrichment.md)<br/>🧩 [`contact_enrichment`](skills/contact_enrichment.md)<br/>⚙️ [`database_mining`](sales/database_mining.md)<br/>🧩 [`email_verification`](skills/email_verification.md)<br/>🤖 [`icp_definition`](sales/icp_definition.md)<br/>🤖 [`list_building`](sales/list_building.md)<br/>🤖 [`market_mapping`](sales/market_mapping.md)<br/>🤖 [`personalization_research`](sales/personalization_research.md)<br/>⚙️ [`social_mining`](sales/social_mining.md)<br/>⚙️ [`web_maps_scraping`](sales/web_maps_scraping.md) |
| 2-capture |  | ⚙️ [`trigger_detection`](sales/trigger_detection.md) | 🤖 [`fit_scoring`](sales/fit_scoring.md) |
| 3-generate |  |  | ⚙️ [`campaign_launch`](sales/campaign_launch.md)<br/>🤖 [`cold_call_scripting`](sales/cold_call_scripting.md)<br/>🤖 [`cold_email_drafting`](sales/cold_email_drafting.md)<br/>🤖 [`linkedin_messaging`](sales/linkedin_messaging.md)<br/>🤖 [`proof_matching`](sales/proof_matching.md)<br/>🤖 [`video_prospecting`](sales/video_prospecting.md) |
| 4-orchestrate | 🤖 [`brand_voice_final_approvals`](sales/brand_voice_final_approvals.md)<br/>🤖 [`deal_strategy_big_accounts`](sales/deal_strategy_big_accounts.md)<br/>🤖 [`key_account_relationships`](sales/key_account_relationships.md)<br/>🤖 [`offer_positioning`](sales/offer_positioning.md) | ⚙️ [`deliverability`](sales/deliverability.md) | 🤖 [`campaign_orchestration`](sales/campaign_orchestration.md)<br/>⚙️ [`send_optimization`](sales/send_optimization.md) |

<details><summary>Full list</summary>

| Stage | Autonomy | Kind | Id | Role | Mode | Produces |
| --- | --- | --- | --- | --- | --- | --- |
| 1-foundation | fully-autonomous | skill | [`account_enrichment`](skills/account_enrichment.md) | — | — | enriched_record |
| 1-foundation | fully-autonomous | skill | [`contact_enrichment`](skills/contact_enrichment.md) | — | — | enriched_record |
| 1-foundation | fully-autonomous | sidecar | [`database_mining`](sales/database_mining.md) | worker | scheduled | enriched_record |
| 1-foundation | fully-autonomous | skill | [`email_verification`](skills/email_verification.md) | — | — | enriched_record |
| 1-foundation | fully-autonomous | agent | [`icp_definition`](sales/icp_definition.md) | analyst | single-shot | markdown_report |
| 1-foundation | fully-autonomous | agent | [`list_building`](sales/list_building.md) | integrator | single-shot | structured_json |
| 1-foundation | fully-autonomous | agent | [`market_mapping`](sales/market_mapping.md) | analyst | single-shot | structured_json |
| 1-foundation | fully-autonomous | agent | [`personalization_research`](sales/personalization_research.md) | analyst | single-shot | structured_json |
| 1-foundation | fully-autonomous | sidecar | [`social_mining`](sales/social_mining.md) | worker | scheduled | enriched_record |
| 1-foundation | fully-autonomous | sidecar | [`web_maps_scraping`](sales/web_maps_scraping.md) | worker | scheduled | enriched_record |
| 1-foundation | human-assisted | agent | [`lookalike_modeling`](sales/lookalike_modeling.md) | analyst | single-shot | markdown_report |
| 2-capture | fully-autonomous | agent | [`fit_scoring`](sales/fit_scoring.md) | classifier | single-shot | structured_json |
| 2-capture | human-assisted | sidecar | [`trigger_detection`](sales/trigger_detection.md) | classifier | event-driven | side_effect |
| 3-generate | fully-autonomous | sidecar | [`campaign_launch`](sales/campaign_launch.md) | connector | event-driven | side_effect |
| 3-generate | fully-autonomous | agent | [`cold_call_scripting`](sales/cold_call_scripting.md) | writer | single-shot | markdown_report |
| 3-generate | fully-autonomous | agent | [`cold_email_drafting`](sales/cold_email_drafting.md) | writer | single-shot | structured_json |
| 3-generate | fully-autonomous | agent | [`linkedin_messaging`](sales/linkedin_messaging.md) | writer | single-shot | structured_json |
| 3-generate | fully-autonomous | agent | [`proof_matching`](sales/proof_matching.md) | analyst | single-shot | structured_json |
| 3-generate | fully-autonomous | agent | [`video_prospecting`](sales/video_prospecting.md) | writer | single-shot | structured_json |
| 4-orchestrate | fully-autonomous | agent | [`campaign_orchestration`](sales/campaign_orchestration.md) | coordinator | event-driven | decision |
| 4-orchestrate | fully-autonomous | sidecar | [`send_optimization`](sales/send_optimization.md) | worker | scheduled | side_effect |
| 4-orchestrate | human-assisted | sidecar | [`deliverability`](sales/deliverability.md) | worker | scheduled | side_effect |
| 4-orchestrate | human-led | agent | [`brand_voice_final_approvals`](sales/brand_voice_final_approvals.md) | reviewer | single-shot | decision |
| 4-orchestrate | human-led | agent | [`deal_strategy_big_accounts`](sales/deal_strategy_big_accounts.md) | analyst | single-shot | markdown_report |
| 4-orchestrate | human-led | agent | [`key_account_relationships`](sales/key_account_relationships.md) | writer | single-shot | markdown_report |
| 4-orchestrate | human-led | agent | [`offer_positioning`](sales/offer_positioning.md) | writer | single-shot | markdown_report |

</details>

### Deals

| Rollout \ Autonomy | human-led | human-assisted | fully-autonomous |
| --- | --- | --- | --- |
| 1-foundation |  |  |  |
| 2-capture |  | 🤖 [`objection_library`](deals/objection_library.md) | ⚙️ [`call_capture`](deals/call_capture.md)<br/>⚙️ [`crm_hygiene`](deals/crm_hygiene.md)<br/>⚙️ [`hot_lead_routing`](deals/hot_lead_routing.md)<br/>⚙️ [`inbox_triage`](deals/inbox_triage.md)<br/>🤖 [`lead_qualification`](deals/lead_qualification.md)<br/>⚙️ [`pipeline_reporting`](deals/pipeline_reporting.md)<br/>🤖 [`post_call_debrief`](deals/post_call_debrief.md)<br/>🤖 [`referral_capture`](deals/referral_capture.md)<br/>🤖 [`reply_classification`](deals/reply_classification.md) |
| 3-generate |  | 🤖 [`agreement_drafting`](deals/agreement_drafting.md)<br/>🤖 [`objection_response`](deals/objection_response.md) | ⚙️ [`comment_cta_fulfillment`](deals/comment_cta_fulfillment.md)<br/>🤖 [`demo_prototyping`](deals/demo_prototyping.md)<br/>🤖 [`follow_up_drafting`](deals/follow_up_drafting.md)<br/>⚙️ [`meeting_booking`](deals/meeting_booking.md)<br/>🤖 [`pre_call_briefing`](deals/pre_call_briefing.md)<br/>🤖 [`pricing_support`](deals/pricing_support.md)<br/>🤖 [`proposal_generation`](deals/proposal_generation.md)<br/>⚙️ [`speed_to_lead`](deals/speed_to_lead.md) |
| 4-orchestrate | 🤖 [`closing_the_deal`](deals/closing_the_deal.md)<br/>🤖 [`discounting_concessions`](deals/discounting_concessions.md)<br/>🤖 [`proposal_final_signoff`](deals/proposal_final_signoff.md)<br/>🤖 [`strategic_account_calls`](deals/strategic_account_calls.md)<br/>🤖 [`win_loss_analysis`](deals/win_loss_analysis.md) | 🤖 [`forecasting`](deals/forecasting.md) | ⚙️ [`deal_room_assembly`](deals/deal_room_assembly.md)<br/>⚙️ [`reactivation`](deals/reactivation.md) |

<details><summary>Full list</summary>

| Stage | Autonomy | Kind | Id | Role | Mode | Produces |
| --- | --- | --- | --- | --- | --- | --- |
| 2-capture | fully-autonomous | sidecar | [`call_capture`](deals/call_capture.md) | worker | event-driven | side_effect |
| 2-capture | fully-autonomous | sidecar | [`crm_hygiene`](deals/crm_hygiene.md) | worker | scheduled | side_effect |
| 2-capture | fully-autonomous | sidecar | [`hot_lead_routing`](deals/hot_lead_routing.md) | connector | event-driven | side_effect |
| 2-capture | fully-autonomous | sidecar | [`inbox_triage`](deals/inbox_triage.md) | classifier | event-driven | side_effect |
| 2-capture | fully-autonomous | agent | [`lead_qualification`](deals/lead_qualification.md) | classifier | event-driven | structured_json |
| 2-capture | fully-autonomous | sidecar | [`pipeline_reporting`](deals/pipeline_reporting.md) | worker | scheduled | side_effect |
| 2-capture | fully-autonomous | agent | [`post_call_debrief`](deals/post_call_debrief.md) | writer | event-driven | markdown_report |
| 2-capture | fully-autonomous | agent | [`referral_capture`](deals/referral_capture.md) | classifier | event-driven | structured_json |
| 2-capture | fully-autonomous | agent | [`reply_classification`](deals/reply_classification.md) | classifier | event-driven | structured_json |
| 2-capture | human-assisted | agent | [`objection_library`](deals/objection_library.md) | analyst | single-shot | structured_json |
| 3-generate | fully-autonomous | sidecar | [`comment_cta_fulfillment`](deals/comment_cta_fulfillment.md) | worker | event-driven | side_effect |
| 3-generate | fully-autonomous | agent | [`demo_prototyping`](deals/demo_prototyping.md) | writer | single-shot | markdown_report |
| 3-generate | fully-autonomous | agent | [`follow_up_drafting`](deals/follow_up_drafting.md) | writer | event-driven | structured_json |
| 3-generate | fully-autonomous | sidecar | [`meeting_booking`](deals/meeting_booking.md) | connector | event-driven | side_effect |
| 3-generate | fully-autonomous | agent | [`pre_call_briefing`](deals/pre_call_briefing.md) | writer | scheduled | markdown_report |
| 3-generate | fully-autonomous | agent | [`pricing_support`](deals/pricing_support.md) | analyst | single-shot | structured_json |
| 3-generate | fully-autonomous | agent | [`proposal_generation`](deals/proposal_generation.md) | writer | single-shot | pdf |
| 3-generate | fully-autonomous | sidecar | [`speed_to_lead`](deals/speed_to_lead.md) | worker | event-driven | side_effect |
| 3-generate | human-assisted | agent | [`agreement_drafting`](deals/agreement_drafting.md) | writer | single-shot | structured_json |
| 3-generate | human-assisted | agent | [`objection_response`](deals/objection_response.md) | writer | single-shot | structured_json |
| 4-orchestrate | fully-autonomous | sidecar | [`deal_room_assembly`](deals/deal_room_assembly.md) | connector | event-driven | side_effect |
| 4-orchestrate | fully-autonomous | sidecar | [`reactivation`](deals/reactivation.md) | worker | scheduled | side_effect |
| 4-orchestrate | human-assisted | agent | [`forecasting`](deals/forecasting.md) | analyst | scheduled | markdown_report |
| 4-orchestrate | human-led | agent | [`closing_the_deal`](deals/closing_the_deal.md) | writer | single-shot | markdown_report |
| 4-orchestrate | human-led | agent | [`discounting_concessions`](deals/discounting_concessions.md) | analyst | single-shot | markdown_report |
| 4-orchestrate | human-led | agent | [`proposal_final_signoff`](deals/proposal_final_signoff.md) | reviewer | single-shot | decision |
| 4-orchestrate | human-led | agent | [`strategic_account_calls`](deals/strategic_account_calls.md) | writer | single-shot | markdown_report |
| 4-orchestrate | human-led | agent | [`win_loss_analysis`](deals/win_loss_analysis.md) | analyst | single-shot | markdown_report |

</details>

### Marketing

| Rollout \ Autonomy | human-led | human-assisted | fully-autonomous |
| --- | --- | --- | --- |
| 1-foundation | 🤖 [`brand_voice_guide`](marketing/brand_voice_guide.md) | 🤖 [`content_calendar`](marketing/content_calendar.md) |  |
| 2-capture |  | 🤖 [`influencer_outreach`](marketing/influencer_outreach.md) | 🤖 [`seo_briefs`](marketing/seo_briefs.md)<br/>⚙️ [`ugc_pipeline`](marketing/ugc_pipeline.md) |
| 3-generate |  | 🤖 [`event_planning`](marketing/event_planning.md)<br/>🤖 [`landing_page_writer`](marketing/landing_page_writer.md)<br/>🤖 [`long_form_content_writer`](marketing/long_form_content_writer.md)<br/>🤖 [`pr_press_kit`](marketing/pr_press_kit.md)<br/>🤖 [`webinar_producer`](marketing/webinar_producer.md) | 🤖 [`ad_creative_generator`](marketing/ad_creative_generator.md)<br/>🤖 [`brief_generation`](marketing/brief_generation.md)<br/>🤖 [`creative_asset_repurpose`](marketing/creative_asset_repurpose.md)<br/>🤖 [`email_nurture_writer`](marketing/email_nurture_writer.md)<br/>🤖 [`social_posts_generator`](marketing/social_posts_generator.md) |
| 4-orchestrate |  | ⚙️ [`community_moderation`](marketing/community_moderation.md)<br/>🤖 [`paid_ads_optimizer`](marketing/paid_ads_optimizer.md) | ⚙️ [`analytics_rollup`](marketing/analytics_rollup.md) |

<details><summary>Full list</summary>

| Stage | Autonomy | Kind | Id | Role | Mode | Produces |
| --- | --- | --- | --- | --- | --- | --- |
| 1-foundation | human-assisted | agent | [`content_calendar`](marketing/content_calendar.md) | coordinator | single-shot | structured_json |
| 1-foundation | human-led | agent | [`brand_voice_guide`](marketing/brand_voice_guide.md) | writer | single-shot | markdown_report |
| 2-capture | fully-autonomous | agent | [`seo_briefs`](marketing/seo_briefs.md) | analyst | single-shot | markdown_report |
| 2-capture | fully-autonomous | sidecar | [`ugc_pipeline`](marketing/ugc_pipeline.md) | worker | event-driven | side_effect |
| 2-capture | human-assisted | agent | [`influencer_outreach`](marketing/influencer_outreach.md) | analyst | single-shot | structured_json |
| 3-generate | fully-autonomous | agent | [`ad_creative_generator`](marketing/ad_creative_generator.md) | writer | single-shot | structured_json |
| 3-generate | fully-autonomous | agent | [`brief_generation`](marketing/brief_generation.md) | writer | single-shot | markdown_report |
| 3-generate | fully-autonomous | agent | [`creative_asset_repurpose`](marketing/creative_asset_repurpose.md) | writer | single-shot | structured_json |
| 3-generate | fully-autonomous | agent | [`email_nurture_writer`](marketing/email_nurture_writer.md) | writer | single-shot | structured_json |
| 3-generate | fully-autonomous | agent | [`social_posts_generator`](marketing/social_posts_generator.md) | writer | single-shot | structured_json |
| 3-generate | human-assisted | agent | [`event_planning`](marketing/event_planning.md) | coordinator | single-shot | markdown_report |
| 3-generate | human-assisted | agent | [`landing_page_writer`](marketing/landing_page_writer.md) | writer | single-shot | markdown_report |
| 3-generate | human-assisted | agent | [`long_form_content_writer`](marketing/long_form_content_writer.md) | writer | single-shot | markdown_report |
| 3-generate | human-assisted | agent | [`pr_press_kit`](marketing/pr_press_kit.md) | writer | single-shot | markdown_report |
| 3-generate | human-assisted | agent | [`webinar_producer`](marketing/webinar_producer.md) | coordinator | single-shot | markdown_report |
| 4-orchestrate | fully-autonomous | sidecar | [`analytics_rollup`](marketing/analytics_rollup.md) | worker | scheduled | side_effect |
| 4-orchestrate | human-assisted | sidecar | [`community_moderation`](marketing/community_moderation.md) | classifier | event-driven | side_effect |
| 4-orchestrate | human-assisted | agent | [`paid_ads_optimizer`](marketing/paid_ads_optimizer.md) | analyst | scheduled | decision |

</details>

### Operations

| Rollout \ Autonomy | human-led | human-assisted | fully-autonomous |
| --- | --- | --- | --- |
| 1-foundation | 🤖 [`architecture_decisions`](operations/architecture_decisions.md)<br/>🤖 [`scope_calls`](operations/scope_calls.md)<br/>🤖 [`sop_generation`](operations/sop_generation.md) | 🧩 [`embeddings_provider`](skills/embeddings_provider.md)<br/>🧩 [`llm_provider`](skills/llm_provider.md)<br/>🧩 [`local_inference`](skills/local_inference.md)<br/>🧩 [`open_model_gateway`](skills/open_model_gateway.md)<br/>🧩 [`vector_store`](skills/vector_store.md)<br/>🧩 [`voicebox_tts`](skills/voicebox_tts.md) |  |
| 2-capture |  | 🤖 [`access_collection`](operations/access_collection.md)<br/>⚙️ [`data_migration`](operations/data_migration.md)<br/>🧩 [`framework_bridge`](skills/framework_bridge.md)<br/>🤖 [`qa_verification`](operations/qa_verification.md) | ⚙️ [`context_maintenance`](operations/context_maintenance.md)<br/>🧩 [`document_extraction`](skills/document_extraction.md)<br/>⚙️ [`transcript_processing`](operations/transcript_processing.md) |
| 3-generate |  | 🤖 [`handoff_docs`](operations/handoff_docs.md)<br/>🤖 [`integration_builds`](operations/integration_builds.md) | 🤖 [`kickoff_pack`](operations/kickoff_pack.md)<br/>🤖 [`meeting_follow_ups`](operations/meeting_follow_ups.md)<br/>⚙️ [`project_scaffolding`](operations/project_scaffolding.md) |
| 4-orchestrate | 🤖 [`client_trust`](operations/client_trust.md)<br/>🤖 [`final_ship_approval`](operations/final_ship_approval.md) | 🤖 [`agent_evaluation`](operations/agent_evaluation.md)<br/>🤖 [`incident_response`](operations/incident_response.md)<br/>⚙️ [`monitoring_alerting`](operations/monitoring_alerting.md) | ⚙️ [`cost_usage_tracking`](operations/cost_usage_tracking.md)<br/>⚙️ [`portal_sync`](operations/portal_sync.md)<br/>🤖 [`status_updates`](operations/status_updates.md) |

<details><summary>Full list</summary>

| Stage | Autonomy | Kind | Id | Role | Mode | Produces |
| --- | --- | --- | --- | --- | --- | --- |
| 1-foundation | human-assisted | skill | [`embeddings_provider`](skills/embeddings_provider.md) | — | — | structured_json |
| 1-foundation | human-assisted | skill | [`llm_provider`](skills/llm_provider.md) | — | — | structured_json |
| 1-foundation | human-assisted | skill | [`local_inference`](skills/local_inference.md) | — | — | structured_json |
| 1-foundation | human-assisted | skill | [`open_model_gateway`](skills/open_model_gateway.md) | — | — | structured_json |
| 1-foundation | human-assisted | skill | [`vector_store`](skills/vector_store.md) | — | — | structured_json |
| 1-foundation | human-assisted | skill | [`voicebox_tts`](skills/voicebox_tts.md) | — | — | structured_json |
| 1-foundation | human-led | agent | [`architecture_decisions`](operations/architecture_decisions.md) | analyst | single-shot | markdown_report |
| 1-foundation | human-led | agent | [`scope_calls`](operations/scope_calls.md) | writer | single-shot | markdown_report |
| 1-foundation | human-led | agent | [`sop_generation`](operations/sop_generation.md) | writer | single-shot | markdown_report |
| 2-capture | fully-autonomous | sidecar | [`context_maintenance`](operations/context_maintenance.md) | worker | scheduled | side_effect |
| 2-capture | fully-autonomous | skill | [`document_extraction`](skills/document_extraction.md) | — | — | structured_json |
| 2-capture | fully-autonomous | sidecar | [`transcript_processing`](operations/transcript_processing.md) | worker | event-driven | side_effect |
| 2-capture | human-assisted | agent | [`access_collection`](operations/access_collection.md) | writer | single-shot | markdown_report |
| 2-capture | human-assisted | sidecar | [`data_migration`](operations/data_migration.md) | worker | event-driven | side_effect |
| 2-capture | human-assisted | skill | [`framework_bridge`](skills/framework_bridge.md) | — | — | structured_json |
| 2-capture | human-assisted | agent | [`qa_verification`](operations/qa_verification.md) | reviewer | single-shot | markdown_report |
| 3-generate | fully-autonomous | agent | [`kickoff_pack`](operations/kickoff_pack.md) | writer | single-shot | pdf |
| 3-generate | fully-autonomous | agent | [`meeting_follow_ups`](operations/meeting_follow_ups.md) | writer | event-driven | structured_json |
| 3-generate | fully-autonomous | sidecar | [`project_scaffolding`](operations/project_scaffolding.md) | connector | event-driven | side_effect |
| 3-generate | human-assisted | agent | [`handoff_docs`](operations/handoff_docs.md) | writer | single-shot | markdown_report |
| 3-generate | human-assisted | agent | [`integration_builds`](operations/integration_builds.md) | writer | single-shot | markdown_report |
| 4-orchestrate | fully-autonomous | sidecar | [`cost_usage_tracking`](operations/cost_usage_tracking.md) | worker | scheduled | side_effect |
| 4-orchestrate | fully-autonomous | sidecar | [`portal_sync`](operations/portal_sync.md) | connector | scheduled | side_effect |
| 4-orchestrate | fully-autonomous | agent | [`status_updates`](operations/status_updates.md) | writer | scheduled | markdown_report |
| 4-orchestrate | human-assisted | agent | [`agent_evaluation`](operations/agent_evaluation.md) | judge | single-shot | structured_json |
| 4-orchestrate | human-assisted | agent | [`incident_response`](operations/incident_response.md) | coordinator | event-driven | markdown_report |
| 4-orchestrate | human-assisted | sidecar | [`monitoring_alerting`](operations/monitoring_alerting.md) | worker | scheduled | side_effect |
| 4-orchestrate | human-led | agent | [`client_trust`](operations/client_trust.md) | writer | single-shot | markdown_report |
| 4-orchestrate | human-led | agent | [`final_ship_approval`](operations/final_ship_approval.md) | reviewer | single-shot | decision |

</details>

### Intelligence

| Rollout \ Autonomy | human-led | human-assisted | fully-autonomous |
| --- | --- | --- | --- |
| 1-foundation | 🤖 [`network_mapping`](intelligence/network_mapping.md)<br/>🤖 [`research_prioritization`](intelligence/research_prioritization.md) |  |  |
| 2-capture | 🤖 [`reading_between_lines`](intelligence/reading_between_lines.md)<br/>🤖 [`warm_intro_pathing`](intelligence/warm_intro_pathing.md) | 🤖 [`buying_committee_mapping`](intelligence/buying_committee_mapping.md)<br/>⚙️ [`warm_path_finding`](intelligence/warm_path_finding.md)<br/>🧩 [`web_extraction`](skills/web_extraction.md) | 🧩 [`funding_financials_lookup`](skills/funding_financials_lookup.md)<br/>🧩 [`tech_stack_detection`](skills/tech_stack_detection.md) |
| 3-generate |  | 🧩 [`model_evaluation`](skills/model_evaluation.md)<br/>🤖 [`tam_market_sizing`](intelligence/tam_market_sizing.md) | 🤖 [`company_deep_dive`](intelligence/company_deep_dive.md)<br/>🤖 [`competitor_teardown`](intelligence/competitor_teardown.md)<br/>🧩 [`data_visualization`](skills/data_visualization.md)<br/>🤖 [`person_research`](intelligence/person_research.md)<br/>🤖 [`pricing_research`](intelligence/pricing_research.md)<br/>🤖 [`research_reports`](intelligence/research_reports.md)<br/>🤖 [`vertical_analysis`](intelligence/vertical_analysis.md) |
| 4-orchestrate | 🤖 [`trusting_the_call`](intelligence/trusting_the_call.md) | ⚙️ [`account_monitoring`](intelligence/account_monitoring.md)<br/>⚙️ [`news_mention_tracking`](intelligence/news_mention_tracking.md) | 🤖 [`adversarial_verification`](intelligence/adversarial_verification.md)<br/>⚙️ [`alert_routing`](intelligence/alert_routing.md) |

<details><summary>Full list</summary>

| Stage | Autonomy | Kind | Id | Role | Mode | Produces |
| --- | --- | --- | --- | --- | --- | --- |
| 1-foundation | human-led | agent | [`network_mapping`](intelligence/network_mapping.md) | analyst | single-shot | structured_json |
| 1-foundation | human-led | agent | [`research_prioritization`](intelligence/research_prioritization.md) | analyst | single-shot | markdown_report |
| 2-capture | fully-autonomous | skill | [`funding_financials_lookup`](skills/funding_financials_lookup.md) | — | — | structured_json |
| 2-capture | fully-autonomous | skill | [`tech_stack_detection`](skills/tech_stack_detection.md) | — | — | structured_json |
| 2-capture | human-assisted | agent | [`buying_committee_mapping`](intelligence/buying_committee_mapping.md) | analyst | single-shot | structured_json |
| 2-capture | human-assisted | sidecar | [`warm_path_finding`](intelligence/warm_path_finding.md) | worker | event-driven | structured_json |
| 2-capture | human-assisted | skill | [`web_extraction`](skills/web_extraction.md) | — | — | structured_json |
| 2-capture | human-led | agent | [`reading_between_lines`](intelligence/reading_between_lines.md) | analyst | single-shot | markdown_report |
| 2-capture | human-led | agent | [`warm_intro_pathing`](intelligence/warm_intro_pathing.md) | analyst | single-shot | markdown_report |
| 3-generate | fully-autonomous | agent | [`company_deep_dive`](intelligence/company_deep_dive.md) | analyst | single-shot | markdown_report |
| 3-generate | fully-autonomous | agent | [`competitor_teardown`](intelligence/competitor_teardown.md) | analyst | single-shot | markdown_report |
| 3-generate | fully-autonomous | skill | [`data_visualization`](skills/data_visualization.md) | — | — | structured_json |
| 3-generate | fully-autonomous | agent | [`person_research`](intelligence/person_research.md) | analyst | single-shot | markdown_report |
| 3-generate | fully-autonomous | agent | [`pricing_research`](intelligence/pricing_research.md) | analyst | single-shot | markdown_report |
| 3-generate | fully-autonomous | agent | [`research_reports`](intelligence/research_reports.md) | writer | single-shot | pdf |
| 3-generate | fully-autonomous | agent | [`vertical_analysis`](intelligence/vertical_analysis.md) | analyst | single-shot | markdown_report |
| 3-generate | human-assisted | skill | [`model_evaluation`](skills/model_evaluation.md) | — | — | structured_json |
| 3-generate | human-assisted | agent | [`tam_market_sizing`](intelligence/tam_market_sizing.md) | analyst | single-shot | markdown_report |
| 4-orchestrate | fully-autonomous | agent | [`adversarial_verification`](intelligence/adversarial_verification.md) | judge | debate | decision |
| 4-orchestrate | fully-autonomous | sidecar | [`alert_routing`](intelligence/alert_routing.md) | connector | event-driven | side_effect |
| 4-orchestrate | human-assisted | sidecar | [`account_monitoring`](intelligence/account_monitoring.md) | worker | scheduled | side_effect |
| 4-orchestrate | human-assisted | sidecar | [`news_mention_tracking`](intelligence/news_mention_tracking.md) | worker | scheduled | side_effect |
| 4-orchestrate | human-led | agent | [`trusting_the_call`](intelligence/trusting_the_call.md) | judge | single-shot | decision |

</details>

### Customer

| Rollout \ Autonomy | human-led | human-assisted | fully-autonomous |
| --- | --- | --- | --- |
| 1-foundation |  |  |  |
| 2-capture |  | ⚙️ [`health_scoring`](customer/health_scoring.md)<br/>🤖 [`ticket_triage`](customer/ticket_triage.md) |  |
| 3-generate |  | 🤖 [`event_coordination`](customer/event_coordination.md) | 🤖 [`engagement_replies`](customer/engagement_replies.md)<br/>🤖 [`faq_self_serve`](customer/faq_self_serve.md)<br/>🤖 [`macro_authoring`](customer/macro_authoring.md)<br/>🤖 [`qbr_prep`](customer/qbr_prep.md) |
| 4-orchestrate | 🤖 [`expansion_playbook`](customer/expansion_playbook.md)<br/>🤖 [`renewal_negotiation`](customer/renewal_negotiation.md)<br/>🤖 [`save_calls`](customer/save_calls.md)<br/>🤖 [`strategic_customer_accounts`](customer/strategic_customer_accounts.md) | 🤖 [`advocacy_referrals`](customer/advocacy_referrals.md)<br/>⚙️ [`churn_prediction`](customer/churn_prediction.md)<br/>⚙️ [`community_moderation_cx`](customer/community_moderation_cx.md)<br/>🤖 [`escalations`](customer/escalations.md) | ⚙️ [`onboarding_journeys`](customer/onboarding_journeys.md) |

<details><summary>Full list</summary>

| Stage | Autonomy | Kind | Id | Role | Mode | Produces |
| --- | --- | --- | --- | --- | --- | --- |
| 2-capture | human-assisted | sidecar | [`health_scoring`](customer/health_scoring.md) | classifier | scheduled | structured_json |
| 2-capture | human-assisted | agent | [`ticket_triage`](customer/ticket_triage.md) | classifier | event-driven | structured_json |
| 3-generate | fully-autonomous | agent | [`engagement_replies`](customer/engagement_replies.md) | writer | event-driven | structured_json |
| 3-generate | fully-autonomous | agent | [`faq_self_serve`](customer/faq_self_serve.md) | writer | event-driven | markdown_report |
| 3-generate | fully-autonomous | agent | [`macro_authoring`](customer/macro_authoring.md) | writer | single-shot | structured_json |
| 3-generate | fully-autonomous | agent | [`qbr_prep`](customer/qbr_prep.md) | writer | single-shot | pptx |
| 3-generate | human-assisted | agent | [`event_coordination`](customer/event_coordination.md) | coordinator | single-shot | markdown_report |
| 4-orchestrate | fully-autonomous | sidecar | [`onboarding_journeys`](customer/onboarding_journeys.md) | worker | event-driven | side_effect |
| 4-orchestrate | human-assisted | agent | [`advocacy_referrals`](customer/advocacy_referrals.md) | analyst | scheduled | structured_json |
| 4-orchestrate | human-assisted | sidecar | [`churn_prediction`](customer/churn_prediction.md) | classifier | scheduled | structured_json |
| 4-orchestrate | human-assisted | sidecar | [`community_moderation_cx`](customer/community_moderation_cx.md) | classifier | event-driven | side_effect |
| 4-orchestrate | human-assisted | agent | [`escalations`](customer/escalations.md) | coordinator | event-driven | markdown_report |
| 4-orchestrate | human-led | agent | [`expansion_playbook`](customer/expansion_playbook.md) | analyst | single-shot | markdown_report |
| 4-orchestrate | human-led | agent | [`renewal_negotiation`](customer/renewal_negotiation.md) | writer | single-shot | markdown_report |
| 4-orchestrate | human-led | agent | [`save_calls`](customer/save_calls.md) | writer | single-shot | markdown_report |
| 4-orchestrate | human-led | agent | [`strategic_customer_accounts`](customer/strategic_customer_accounts.md) | writer | single-shot | markdown_report |

</details>

### Back Office

| Rollout \ Autonomy | human-led | human-assisted | fully-autonomous |
| --- | --- | --- | --- |
| 1-foundation |  |  |  |
| 2-capture | 🤖 [`candidate_sourcing`](back-office/candidate_sourcing.md)<br/>🤖 [`entity_compliance`](back-office/entity_compliance.md) | ⚙️ [`expense_categorization`](back-office/expense_categorization.md)<br/>⚙️ [`screening_scheduling`](back-office/screening_scheduling.md) | ⚙️ [`crm_sync`](back-office/crm_sync.md)<br/>⚙️ [`document_filing`](back-office/document_filing.md)<br/>⚙️ [`email_triage_office`](back-office/email_triage_office.md)<br/>⚙️ [`payment_tracking`](back-office/payment_tracking.md) |
| 3-generate |  | 🤖 [`hr_policy_assistant`](back-office/hr_policy_assistant.md) | 🤖 [`invoice_generation`](back-office/invoice_generation.md)<br/>🤖 [`onboarding_training`](back-office/onboarding_training.md) |
| 4-orchestrate | 🤖 [`banking_operations`](back-office/banking_operations.md)<br/>🤖 [`compliance_signoff`](back-office/compliance_signoff.md)<br/>🤖 [`hiring_decisions`](back-office/hiring_decisions.md)<br/>🤖 [`spend_authority`](back-office/spend_authority.md) | 🤖 [`cash_flow_forecasting`](back-office/cash_flow_forecasting.md)<br/>🤖 [`collections`](back-office/collections.md)<br/>⚙️ [`contract_lifecycle`](back-office/contract_lifecycle.md) | ⚙️ [`budget_tracking`](back-office/budget_tracking.md)<br/>⚙️ [`calendar_management`](back-office/calendar_management.md)<br/>⚙️ [`goal_pacing`](back-office/goal_pacing.md)<br/>⚙️ [`revenue_reporting`](back-office/revenue_reporting.md) |

<details><summary>Full list</summary>

| Stage | Autonomy | Kind | Id | Role | Mode | Produces |
| --- | --- | --- | --- | --- | --- | --- |
| 2-capture | fully-autonomous | sidecar | [`crm_sync`](back-office/crm_sync.md) | connector | scheduled | side_effect |
| 2-capture | fully-autonomous | sidecar | [`document_filing`](back-office/document_filing.md) | worker | event-driven | side_effect |
| 2-capture | fully-autonomous | sidecar | [`email_triage_office`](back-office/email_triage_office.md) | classifier | event-driven | side_effect |
| 2-capture | fully-autonomous | sidecar | [`payment_tracking`](back-office/payment_tracking.md) | worker | scheduled | side_effect |
| 2-capture | human-assisted | sidecar | [`expense_categorization`](back-office/expense_categorization.md) | classifier | scheduled | side_effect |
| 2-capture | human-assisted | sidecar | [`screening_scheduling`](back-office/screening_scheduling.md) | connector | event-driven | side_effect |
| 2-capture | human-led | agent | [`candidate_sourcing`](back-office/candidate_sourcing.md) | analyst | single-shot | structured_json |
| 2-capture | human-led | agent | [`entity_compliance`](back-office/entity_compliance.md) | analyst | scheduled | markdown_report |
| 3-generate | fully-autonomous | agent | [`invoice_generation`](back-office/invoice_generation.md) | writer | event-driven | pdf |
| 3-generate | fully-autonomous | agent | [`onboarding_training`](back-office/onboarding_training.md) | writer | event-driven | markdown_report |
| 3-generate | human-assisted | agent | [`hr_policy_assistant`](back-office/hr_policy_assistant.md) | writer | event-driven | markdown_report |
| 4-orchestrate | fully-autonomous | sidecar | [`budget_tracking`](back-office/budget_tracking.md) | worker | scheduled | side_effect |
| 4-orchestrate | fully-autonomous | sidecar | [`calendar_management`](back-office/calendar_management.md) | worker | event-driven | side_effect |
| 4-orchestrate | fully-autonomous | sidecar | [`goal_pacing`](back-office/goal_pacing.md) | worker | scheduled | side_effect |
| 4-orchestrate | fully-autonomous | sidecar | [`revenue_reporting`](back-office/revenue_reporting.md) | worker | scheduled | side_effect |
| 4-orchestrate | human-assisted | agent | [`cash_flow_forecasting`](back-office/cash_flow_forecasting.md) | analyst | scheduled | markdown_report |
| 4-orchestrate | human-assisted | agent | [`collections`](back-office/collections.md) | writer | scheduled | markdown_report |
| 4-orchestrate | human-assisted | sidecar | [`contract_lifecycle`](back-office/contract_lifecycle.md) | worker | event-driven | side_effect |
| 4-orchestrate | human-led | agent | [`banking_operations`](back-office/banking_operations.md) | writer | single-shot | markdown_report |
| 4-orchestrate | human-led | agent | [`compliance_signoff`](back-office/compliance_signoff.md) | reviewer | single-shot | decision |
| 4-orchestrate | human-led | agent | [`hiring_decisions`](back-office/hiring_decisions.md) | writer | single-shot | markdown_report |
| 4-orchestrate | human-led | agent | [`spend_authority`](back-office/spend_authority.md) | reviewer | single-shot | decision |

</details>

## Vertical adapters

Cards tuned to a specific vertical. They complement the domain-agnostic ops catalogue above — e.g. a real-estate agency uses generic `contact_enrichment` plus its own `property_dossier`.

### Real Estate agency

| Stage | Autonomy | Kind | Id | Role | Mode | Produces |
| --- | --- | --- | --- | --- | --- | --- |
| 2-capture | fully-autonomous | agent | [`buyer_matching`](verticals/real-estate/buyer_matching.md) | classifier | scheduled | structured_json |
| 2-capture | fully-autonomous | agent | [`mortgage_prequal`](verticals/real-estate/mortgage_prequal.md) | analyst | single-shot | markdown_report |
| 3-generate | fully-autonomous | agent | [`listing_generator`](verticals/real-estate/listing_generator.md) | writer | single-shot | structured_json |
| 3-generate | fully-autonomous | agent | [`property_dossier`](verticals/real-estate/property_dossier.md) | analyst | single-shot | pdf |
| 3-generate | human-assisted | agent | [`offer_letter_drafting`](verticals/real-estate/offer_letter_drafting.md) | writer | single-shot | pdf |
| 3-generate | human-assisted | sidecar | [`open_house_coordination`](verticals/real-estate/open_house_coordination.md) | connector | event-driven | side_effect |
| 4-orchestrate | human-assisted | agent | [`closing_coordination`](verticals/real-estate/closing_coordination.md) | coordinator | single-shot | markdown_report |

### Marketing agency

| Stage | Autonomy | Kind | Id | Role | Mode | Produces |
| --- | --- | --- | --- | --- | --- | --- |
| 2-capture | fully-autonomous | sidecar | [`timesheet_reconciliation`](verticals/marketing-agency/timesheet_reconciliation.md) | worker | scheduled | side_effect |
| 2-capture | human-assisted | agent | [`scope_change_control`](verticals/marketing-agency/scope_change_control.md) | writer | single-shot | markdown_report |
| 3-generate | human-assisted | agent | [`pitch_deck_generator`](verticals/marketing-agency/pitch_deck_generator.md) | writer | single-shot | pptx |
| 4-orchestrate | fully-autonomous | agent | [`client_reporting`](verticals/marketing-agency/client_reporting.md) | writer | scheduled | pdf |
| 4-orchestrate | human-assisted | sidecar | [`creative_approval_flow`](verticals/marketing-agency/creative_approval_flow.md) | connector | event-driven | side_effect |
| 4-orchestrate | human-assisted | agent | [`creative_pipeline`](verticals/marketing-agency/creative_pipeline.md) | coordinator | scheduled | markdown_report |

### Night club

| Stage | Autonomy | Kind | Id | Role | Mode | Produces |
| --- | --- | --- | --- | --- | --- | --- |
| 2-capture | fully-autonomous | sidecar | [`bar_inventory`](verticals/nightclub/bar_inventory.md) | worker | scheduled | side_effect |
| 2-capture | fully-autonomous | sidecar | [`guest_list_management`](verticals/nightclub/guest_list_management.md) | worker | event-driven | side_effect |
| 2-capture | fully-autonomous | agent | [`reservation_handling`](verticals/nightclub/reservation_handling.md) | writer | event-driven | markdown_report |
| 2-capture | human-assisted | sidecar | [`incident_book`](verticals/nightclub/incident_book.md) | worker | event-driven | side_effect |
| 3-generate | fully-autonomous | agent | [`social_night_recap`](verticals/nightclub/social_night_recap.md) | writer | event-driven | structured_json |
| 3-generate | human-assisted | agent | [`bottle_service_pricing`](verticals/nightclub/bottle_service_pricing.md) | analyst | single-shot | markdown_report |
| 3-generate | human-assisted | agent | [`dj_booking_pipeline`](verticals/nightclub/dj_booking_pipeline.md) | coordinator | single-shot | markdown_report |
| 4-orchestrate | human-led | agent | [`licensing_compliance`](verticals/nightclub/licensing_compliance.md) | analyst | scheduled | markdown_report |

## Gates

| Id | Category | Domain |
| --- | --- | --- |
| [`scaling_gate_definer`](validation/scaling_gate_definer.md) | validation | — |
| [`strategic_decision_gate`](market-research/strategic_decision_gate.md) | market-research | — |

## Optional templates

| Id | Category | Domain |
| --- | --- | --- |
| [`embeddings_provider`](skills/embeddings_provider.md) | operations | operations |
| [`framework_bridge`](skills/framework_bridge.md) | operations | operations |
| [`fundraising_strategist`](scaling/fundraising_strategist.md) | scaling | — |
| [`llm_provider`](skills/llm_provider.md) | operations | operations |
| [`mobile_app_specifier`](scaling/mobile_app_specifier.md) | scaling | — |
| [`model_evaluation`](skills/model_evaluation.md) | operations | intelligence |
| [`open_model_gateway`](skills/open_model_gateway.md) | operations | operations |
| [`startup_valuation_analyst`](scaling/startup_valuation_analyst.md) | scaling | — |
| [`vector_store`](skills/vector_store.md) | operations | operations |
| [`voicebox_tts`](skills/voicebox_tts.md) | operations | operations |
| [`web_extraction`](skills/web_extraction.md) | operations | intelligence |

## Index by role

| Role | Count | Templates |
| --- | ---: | --- |
| `analyst` | 61 | `advocacy_referrals`, `architecture_decisions`, `bottle_service_pricing`, `buying_committee_mapping`, `candidate_sourcing`, `cash_flow_forecasting`, `channel_economics_modeler`, `company_deep_dive`, … (+53) |
| `classifier` | 14 | `buyer_matching`, `churn_prediction`, `community_moderation`, `community_moderation_cx`, `email_triage_office`, `expense_categorization`, `fit_scoring`, `health_scoring`, … (+6) |
| `connector` | 11 | `alert_routing`, `campaign_launch`, `creative_approval_flow`, `crm_sync`, `deal_room_assembly`, `hot_lead_routing`, `meeting_booking`, `open_house_coordination`, … (+3) |
| `coordinator` | 10 | `campaign_orchestration`, `closing_coordination`, `content_calendar`, `creative_pipeline`, `dj_booking_pipeline`, `escalations`, `event_coordination`, `event_planning`, … (+2) |
| `debater` | 2 | `bull_bear_debate_pair`, `risk_committee` |
| `integrator` | 3 | `list_building`, `tranche_0_budgeter`, `tranche_1_budgeter` |
| `judge` | 5 | `adversarial_verification`, `agent_evaluation`, `scaling_gate_definer`, `strategic_decision_gate`, `trusting_the_call` |
| `reflector` | 1 | `memory_reflector` |
| `reviewer` | 6 | `brand_voice_final_approvals`, `compliance_signoff`, `final_ship_approval`, `proposal_final_signoff`, `qa_verification`, `spend_authority` |
| `worker` | 33 | `account_monitoring`, `analytics_rollup`, `bar_inventory`, `budget_tracking`, `calendar_management`, `call_capture`, `comment_cta_fulfillment`, `context_maintenance`, … (+25) |
| `writer` | 67 | `access_collection`, `ad_creative_generator`, `agreement_drafting`, `banking_operations`, `brand_identity_writer`, `brand_voice_guide`, `brief_generation`, `client_reporting`, … (+59) |
| `—` | 16 | `account_enrichment`, `contact_enrichment`, `data_visualization`, `document_extraction`, `email_verification`, `embeddings_provider`, `framework_bridge`, `funding_financials_lookup`, … (+8) |

## Index by tag

| Tag | Templates |
| --- | --- |
| `acceptance` | `functional_specifier` |
| `access` | `access_collection` |
| `account` | `account_enrichment` |
| `accounting` | `expense_categorization` |
| `accounts` | `account_monitoring`, `market_mapping` |
| `adoption` | `market_trends_timing_analyst` |
| `adr` | `architecture_decisions` |
| `ads` | `ad_creative_generator` |
| `adversarial` | `adversarial_verification` |
| `advocacy` | `advocacy_referrals` |
| `ae-assisted` | `objection_response` |
| `ae-led` | `closing_the_deal`, `discounting_concessions`, `proposal_final_signoff`, `strategic_account_calls` |
| `agency` | `brief_generation`, `client_reporting`, `creative_approval_flow`, `creative_pipeline`, `pitch_deck_generator`, `scope_change_control`, … (+1) |
| `alerting` | `monitoring_alerting` |
| `alerts` | `alert_routing` |
| `alive-cost` | `minimal_tech_stack_cost_estimator` |
| `analyst-led` | `reading_between_lines`, `research_prioritization`, `trusting_the_call` |
| `analytics` | `analytics_rollup` |
| `android` | `mobile_app_specifier` |
| `anthropic` | `llm_provider` |
| `api` | `integration_builds` |
| `approval` | `creative_approval_flow`, `final_ship_approval`, `proposal_final_signoff`, `spend_authority` |
| `ar` | `collections` |
| `architecture` | `architecture_decisions`, `platform_areas_architect` |
| `areas` | `platform_areas_architect` |
| `assignment` | `hot_lead_routing` |
| `atomization` | `creative_asset_repurpose` |
| `bandit` | `campaign_orchestration` |
| `banking` | `banking_operations` |
| `bant` | `lead_qualification` |
| `bar` | `bar_inventory` |
| `bear` | `bull_bear_debate_pair` |
| `bedrock` | `llm_provider` |
| `benchmarks` | `channel_economics_modeler` |
| `berkus` | `startup_valuation_analyst` |
| `big-accounts` | `deal_strategy_big_accounts` |
| `billing` | `invoice_generation`, `timesheet_reconciliation` |
| `blog` | `long_form_content_writer` |
| `blue-ocean` | `market_gap_analyst` |
| `board` | `revenue_reporting` |
| `booking` | `dj_booking_pipeline` |
| `bottle-service` | `bottle_service_pricing` |
| `brain` | `context_maintenance` |
| `brand` | `brand_identity_writer`, `news_mention_tracking` |
| `brand-voice` | `brand_voice_final_approvals`, `brand_voice_guide` |
| `brief` | `brief_generation`, `seo_briefs` |
| `briefing` | `pre_call_briefing` |
| `browser` | `local_inference` |
| `budget` | `budget_tracking`, `tranche_0_budgeter`, `tranche_1_budgeter` |
| `build-vs-buy` | `tech_stack_vendors_analyst` |
| `bull` | `bull_bear_debate_pair` |
| `burn` | `budget_tracking` |
| `business-plan` | `financial_business_planner` |
| `buyers` | `buyer_matching` |
| `cac` | `channel_economics_modeler`, `ltv_cac_targeter` |
| `cac-ltv` | `scaling_gate_definer` |
| `calendar` | `calendar_management`, `content_calendar`, `tranche_1_budgeter` |
| `call` | `call_capture`, `post_call_debrief` |
| `campaign` | `campaign_launch`, `campaign_orchestration` |
| `cap-table` | `resource_inventory_analyst` |
| `capacity` | `creative_pipeline` |
| `capital` | `tranche_0_budgeter`, `tranche_1_budgeter` |
| `capture` | `referral_capture` |
| `case-study` | `proof_matching` |
| `cash-flow` | `cash_flow_forecasting`, `tranche_0_budgeter` |
| `cassandra` | `vector_store` |
| `change-order` | `scope_change_control` |
| `channels` | `channel_economics_modeler` |
| `chart` | `data_visualization`, `market_research_analyst` |
| `chat` | `llm_provider` |
| `checkpoint` | `scaling_gate_definer`, `strategic_decision_gate` |
| `chroma` | `vector_store` |
| `churn` | `churn_prediction`, `save_calls` |
| `classification` | `reply_classification` |
| `cleanup` | `crm_hygiene` |
| `client` | `client_reporting` |
| `client-comms` | `client_trust` |
| `closed-lost` | `reactivation` |
| `closing` | `closing_coordination`, `closing_the_deal` |
| `cloud` | `tech_stack_vendors_analyst` |
| `cohere` | `embeddings_provider`, `llm_provider` |
| `cold` | `cold_email_drafting` |
| `cold-call` | `cold_call_scripting` |
| `collections` | `collections` |
| `committee` | `buying_committee_mapping`, `risk_committee` |
| `community` | `community_moderation`, `community_moderation_cx` |
| `comparables` | `startup_valuation_analyst` |
| `competition` | `competitive_analyst` |
| `competitive` | `pricing_research` |
| `competitor` | `competitor_teardown` |
| `compliance` | `compliance_signoff`, `entity_compliance`, `licensing_compliance` |
| `concession` | `discounting_concessions` |
| `connector` | `crm_sync` |
| `contact` | `contact_enrichment` |
| `content` | `creative_asset_repurpose`, `long_form_content_writer`, `seo_briefs`, `ugc_pipeline`, `validation_experiment_designer` |
| `context` | `context_maintenance` |
| `contract` | `agreement_drafting`, `contract_lifecycle`, `offer_letter_drafting` |
| `copy` | `ad_creative_generator`, `cold_email_drafting`, `landing_page_writer` |
| `cost` | `cost_usage_tracking` |
| `country` | `market_study_by_country_analyst` |
| `cpc` | `channel_economics_modeler` |
| `cpl` | `channel_economics_modeler` |
| `cpm` | `channel_economics_modeler` |
| `crawl4ai` | `web_extraction` |
| `creative` | `ad_creative_generator`, `brief_generation`, `creative_approval_flow` |
| `creator` | `influencer_outreach` |
| `credentials` | `access_collection` |
| `crm` | `crm_hygiene`, `crm_sync` |
| `csm` | `health_scoring`, `qbr_prep` |
| `csm-led` | `expansion_playbook`, `renewal_negotiation`, `save_calls`, `strategic_customer_accounts` |
| `cta` | `comment_cta_fulfillment` |
| `customer` | `event_coordination`, `market_customer_profiler` |
| `cx` | `community_moderation_cx`, `escalations`, `ticket_triage` |
| `dafo` | `swot_analyst` |
| `dashboard` | `pipeline_reporting` |
| `data-extraction` | `web_extraction` |
| `data-model` | `data_schema_designer` |
| `database` | `database_mining` |
| `dcf` | `startup_valuation_analyst` |
| `deal-room` | `deal_room_assembly` |
| `debate` | `bull_bear_debate_pair` |
| `debrief` | `post_call_debrief` |
| `decision` | `trusting_the_call` |
| `deep-dive` | `company_deep_dive` |
| `deepeval` | `model_evaluation` |
| `deliverability` | `deliverability`, `email_verification`, `send_optimization` |
| `demo` | `demo_prototyping` |
| `dependencies` | `risk_assessor` |
| `digest` | `analytics_rollup` |
| `discount` | `discounting_concessions` |
| `dj` | `dj_booking_pipeline` |
| `dkim` | `deliverability` |
| `dm` | `linkedin_messaging` |
| `dmarc` | `deliverability` |
| `docling` | `web_extraction` |
| `documentation` | `handoff_docs` |
| `documents` | `document_extraction`, `document_filing` |
| `docx` | `project_intake_facilitator` |
| `door` | `guest_list_management` |
| `dossier` | `person_research`, `property_dossier` |
| `dpa` | `legal_ip_analyst` |
| `drafting` | `agreement_drafting` |
| `eaa` | `calendar_management` |
| `elasticity` | `pricing_strategist` |
| `email` | `cold_email_drafting`, `deliverability`, `email_nurture_writer`, `email_verification`, `follow_up_drafting` |
| `embeddings` | `embeddings_provider` |
| `enablement` | `objection_library` |
| `engagement` | `deal_room_assembly` |
| `enrichment` | `account_enrichment`, `contact_enrichment` |
| `entities` | `data_schema_designer` |
| `entity` | `entity_compliance` |
| `equity` | `fundamental_analyst`, `market_research_analyst` |
| `escalation` | `escalations` |
| `escrow` | `closing_coordination` |
| `etl` | `data_migration` |
| `evals` | `agent_evaluation` |
| `evaluation` | `model_evaluation` |
| `events` | `event_coordination`, `event_planning`, `webinar_producer` |
| `exec` | `email_triage_office` |
| `executive-summary` | `executive_summary_writer` |
| `expansion` | `expansion_playbook` |
| `expense` | `expense_categorization` |
| `experiments` | `validation_experiment_designer` |
| `extraction` | `document_extraction` |
| `extractthinker` | `web_extraction` |
| `features` | `competitive_analyst` |
| `filing` | `document_filing` |
| `filings` | `fundamental_analyst` |
| `finance` | `bull_bear_debate_pair`, `fundamental_analyst`, `macro_context_agent`, `market_research_analyst`, `memory_reflector`, `risk_committee` |
| `financials` | `financial_business_planner`, `financial_excel_builder`, `funding_financials_lookup` |
| `finops` | `cost_usage_tracking` |
| `firecrawl` | `web_extraction` |
| `firmographics` | `account_enrichment`, `icp_definition` |
| `fit` | `fit_scoring` |
| `flows` | `data_schema_designer` |
| `follow-up` | `follow_up_drafting`, `meeting_follow_ups` |
| `forecast` | `cash_flow_forecasting`, `forecasting` |
| `founder-led` | `banking_operations`, `brand_voice_final_approvals`, `brand_voice_guide`, `candidate_sourcing`, `compliance_signoff`, `deal_strategy_big_accounts`, … (+6) |
| `founder-onboarding` | `project_intake_facilitator` |
| `framework` | `framework_bridge` |
| `fred` | `macro_context_agent` |
| `functional-spec` | `functional_specifier` |
| `fundamentals` | `fundamental_analyst` |
| `funding` | `funding_financials_lookup` |
| `fundraising` | `fundraising_strategist` |
| `gap` | `market_gap_analyst` |
| `gate` | `final_ship_approval`, `strategic_decision_gate` |
| `gate-1` | `scaling_gate_definer` |
| `gdpr` | `legal_ip_analyst` |
| `gemini` | `llm_provider` |
| `gemma3` | `open_model_gateway` |
| `geo` | `market_study_by_country_analyst`, `web_maps_scraping` |
| `giskard` | `model_evaluation` |
| `go-no-go` | `strategic_decision_gate` |
| `go-to-market` | `gtm_strategist` |
| `google` | `embeddings_provider` |
| `graph` | `network_mapping` |
| `groq` | `llm_provider` |
| `gtm` | `gtm_strategist` |
| `guest-list` | `guest_list_management` |
| `handoff` | `handoff_docs` |
| `haystack` | `framework_bridge` |
| `health` | `health_scoring` |
| `helpdesk` | `engagement_replies`, `macro_authoring` |
| `hiring` | `candidate_sourcing`, `financial_business_planner`, `hiring_decisions`, `screening_scheduling` |
| `hooks` | `personalization_research` |
| `hr` | `hr_policy_assistant`, `onboarding_training` |
| `huggingface` | `open_model_gateway` |
| `hygiene` | `crm_hygiene` |
| `hypothesis` | `validation_hypotheses_analyst` |
| `iam` | `user_roles_permissions_writer` |
| `icp` | `fit_scoring`, `icp_definition` |
| `identity` | `brand_identity_writer` |
| `in-scope` | `mvp_scoper` |
| `inbound` | `comment_cta_fulfillment`, `speed_to_lead` |
| `inbox` | `email_triage_office`, `inbox_triage` |
| `incident` | `incident_book`, `incident_response` |
| `incorporation` | `legal_setup_cost_estimator` |
| `index` | `context_maintenance` |
| `inference` | `local_inference` |
| `influencer` | `influencer_outreach` |
| `information-architecture` | `ux_platform_designer` |
| `intake` | `project_intake_facilitator` |
| `integration` | `embeddings_provider`, `framework_bridge`, `integration_builds`, `llm_provider`, `model_evaluation`, `open_model_gateway`, … (+2) |
| `interpretation` | `reading_between_lines` |
| `inventory` | `bar_inventory`, `resource_inventory_analyst` |
| `investor` | `pitch_deck_designer` |
| `investors` | `fundraising_strategist` |
| `invoice` | `invoice_generation` |
| `ios` | `mobile_app_specifier` |
| `ip` | `legal_ip_analyst` |
| `judge` | `bull_bear_debate_pair` |
| `judgement` | `trusting_the_call` |
| `kb` | `faq_self_serve` |
| `kickoff` | `kickoff_pack`, `project_scaffolding` |
| `kpi` | `goal_pacing`, `kpis_okrs_framework_writer` |
| `landing` | `validation_experiment_designer` |
| `landing-page` | `landing_page_writer` |
| `landscape` | `market_mapping` |
| `langchain` | `framework_bridge` |
| `launch` | `campaign_launch`, `gtm_strategist` |
| `legal` | `legal_ip_analyst`, `legal_setup_cost_estimator` |
| `library` | `objection_library` |
| `licensing` | `licensing_compliance` |
| `lifecycle` | `contract_lifecycle`, `email_nurture_writer`, `onboarding_journeys` |
| `linkedin` | `linkedin_messaging`, `social_mining` |
| `list` | `list_building` |
| `listing` | `listing_generator` |
| `litertjs` | `local_inference` |
| `llama4` | `open_model_gateway` |
| `llamaindex` | `framework_bridge` |
| `llamaparse` | `web_extraction` |
| `llm` | `llm_provider` |
| `local` | `open_model_gateway`, `voicebox_tts`, `web_maps_scraping` |
| `logo` | `brand_identity_writer` |
| `long-form` | `long_form_content_writer` |
| `lookalike` | `lookalike_modeling` |
| `loom` | `video_prospecting` |
| `ltv` | `ltv_cac_targeter` |
| `macro` | `macro_authoring`, `macro_context_agent` |
| `maps` | `web_maps_scraping` |
| `market` | `competitive_analyst`, `market_customer_profiler`, `market_problem_analyst`, `market_study_by_country_analyst`, `market_trends_timing_analyst` |
| `market-map` | `market_mapping` |
| `market-sizing` | `tam_market_sizing` |
| `matching` | `buyer_matching` |
| `matrix` | `risk_assessor` |
| `mcp` | `framework_bridge`, `voicebox_tts` |
| `meddpicc` | `buying_committee_mapping`, `lead_qualification` |
| `meeting` | `meeting_booking` |
| `meetings` | `meeting_follow_ups`, `transcript_processing` |
| `megaparser` | `web_extraction` |
| `memory` | `memory_reflector` |
| `messaging` | `linkedin_messaging` |
| `metrics` | `kpis_okrs_framework_writer` |
| `migration` | `data_migration` |
| `milestones` | `product_roadmap_writer` |
| `milvus` | `vector_store` |
| `mining` | `database_mining` |
| `mistral` | `llm_provider` |
| `mitigation` | `risk_assessor` |
| `mobile` | `mobile_app_specifier` |
| `modeling` | `lookalike_modeling` |
| `moderation` | `community_moderation`, `community_moderation_cx` |
| `modules` | `platform_areas_architect` |
| `monetization` | `pricing_strategist` |
| `monitoring` | `account_monitoring`, `monitoring_alerting`, `news_mention_tracking` |
| `mortgage` | `mortgage_prequal` |
| `motion` | `gtm_strategist` |
| `mvp` | `minimal_tech_stack_cost_estimator`, `mvp_scoper` |
| `mvs` | `resource_inventory_analyst` |
| `naming` | `brand_identity_writer` |
| `navigation` | `ux_platform_designer` |
| `network` | `network_mapping`, `warm_intro_pathing`, `warm_path_finding` |
| `new-business` | `pitch_deck_generator` |
| `news` | `news_mention_tracking` |
| `nightclub` | `bar_inventory`, `bottle_service_pricing`, `dj_booking_pipeline`, `guest_list_management`, `incident_book`, `licensing_compliance`, … (+2) |
| `nomic` | `embeddings_provider` |
| `north-star` | `kpis_okrs_framework_writer` |
| `nurture` | `email_nurture_writer` |
| `objection` | `objection_response` |
| `objections` | `objection_library` |
| `offer` | `offer_letter_drafting`, `offer_positioning` |
| `okr` | `kpis_okrs_framework_writer` |
| `ollama` | `open_model_gateway` |
| `onboarding` | `access_collection`, `kickoff_pack`, `onboarding_journeys`, `onboarding_training` |
| `one-pager` | `executive_summary_writer` |
| `open-house` | `open_house_coordination` |
| `open-model` | `open_model_gateway` |
| `openai` | `embeddings_provider`, `llm_provider` |
| `openbb` | `fundamental_analyst`, `macro_context_agent`, `market_research_analyst` |
| `opensearch` | `vector_store` |
| `operator-led` | `architecture_decisions`, `client_trust`, `final_ship_approval`, `scope_calls`, `sop_generation` |
| `optimization` | `paid_ads_optimizer` |
| `optional` | `fundraising_strategist`, `mobile_app_specifier`, `startup_valuation_analyst` |
| `orchestration` | `campaign_orchestration` |
| `out-of-scope` | `mvp_scoper` |
| `outbound` | `campaign_launch`, `validation_experiment_designer` |
| `outcome` | `memory_reflector` |
| `outreach` | `influencer_outreach`, `list_building` |
| `pacing` | `goal_pacing` |
| `paid-ads` | `paid_ads_optimizer` |
| `pain-points` | `market_problem_analyst` |
| `payments` | `payment_tracking` |
| `pdf` | `executive_summary_writer`, `proposal_generation`, `research_reports` |
| `permissions` | `user_roles_permissions_writer` |
| `person` | `person_research` |
| `personalization` | `personalization_research` |
| `personas` | `market_customer_profiler` |
| `pgvector` | `vector_store` |
| `phase-1` | `brand_identity_writer`, `competitive_analyst`, `market_customer_profiler`, `market_gap_analyst`, `market_problem_analyst`, `market_study_by_country_analyst`, … (+4) |
| `phase-2` | `legal_setup_cost_estimator`, `minimal_tech_stack_cost_estimator`, `mvp_scoper`, `resource_inventory_analyst`, `tranche_0_budgeter` |
| `phase-3` | `channel_economics_modeler`, `ltv_cac_targeter`, `scaling_gate_definer`, `tranche_1_budgeter`, `validation_experiment_designer`, `validation_hypotheses_analyst` |
| `phase-4` | `data_schema_designer`, `executive_summary_writer`, `financial_business_planner`, `financial_excel_builder`, `functional_specifier`, `fundraising_strategist`, … (+11) |
| `phase-5` | `pitch_deck_designer` |
| `phase-boundary` | `scaling_gate_definer`, `strategic_decision_gate`, `tranche_0_budgeter` |
| `phi4` | `open_model_gateway` |
| `pinecone` | `vector_store` |
| `pipeline` | `creative_pipeline`, `forecasting`, `pipeline_reporting` |
| `pitch` | `pitch_deck_generator` |
| `pitch-deck` | `pitch_deck_designer` |
| `pivot` | `strategic_decision_gate` |
| `planning` | `content_calendar`, `event_planning` |
| `platform` | `platform_areas_architect` |
| `policy` | `hr_policy_assistant` |
| `portal` | `portal_sync` |
| `portals` | `listing_generator` |
| `portfolio-manager` | `risk_committee` |
| `positioning` | `competitive_analyst`, `offer_positioning` |
| `postmortem` | `incident_response`, `memory_reflector`, `win_loss_analysis` |
| `posts` | `social_posts_generator` |
| `pptx` | `pitch_deck_designer` |
| `pr` | `pr_press_kit` |
| `prediction` | `churn_prediction` |
| `prep` | `demo_prototyping`, `pre_call_briefing` |
| `prequal` | `mortgage_prequal` |
| `press` | `pr_press_kit` |
| `pricing` | `bottle_service_pricing`, `competitive_analyst`, `pricing_research`, `pricing_strategist`, `pricing_support` |
| `prioritization` | `list_building` |
| `problem` | `market_problem_analyst` |
| `process` | `sop_generation` |
| `projections` | `financial_excel_builder` |
| `proof` | `proof_matching` |
| `property` | `property_dossier` |
| `proposal` | `proposal_final_signoff`, `proposal_generation` |
| `prospecting` | `video_prospecting` |
| `provisioning` | `project_scaffolding` |
| `pwa` | `mobile_app_specifier` |
| `qa` | `qa_verification` |
| `qbr` | `qbr_prep` |
| `qdrant` | `vector_store` |
| `quadrant` | `market_gap_analyst` |
| `qualification` | `lead_qualification` |
| `quality` | `adversarial_verification` |
| `quality-gate` | `agent_evaluation` |
| `quarters` | `product_roadmap_writer` |
| `questionnaire` | `project_intake_facilitator` |
| `quote` | `pricing_support` |
| `qwen3` | `open_model_gateway` |
| `ragas` | `model_evaluation` |
| `rates` | `macro_context_agent` |
| `rbac` | `user_roles_permissions_writer` |
| `reactivation` | `reactivation` |
| `real-estate` | `buyer_matching`, `closing_coordination`, `listing_generator`, `mortgage_prequal`, `offer_letter_drafting`, `open_house_coordination`, … (+1) |
| `recap` | `social_night_recap` |
| `reconciliation` | `payment_tracking` |
| `redlines` | `agreement_drafting` |
| `referral` | `advocacy_referrals`, `referral_capture` |
| `reflection` | `memory_reflector` |
| `relationships` | `key_account_relationships` |
| `release` | `pr_press_kit` |
| `renewal` | `renewal_negotiation` |
| `reply` | `engagement_replies`, `reply_classification` |
| `report` | `research_reports` |
| `reporting` | `client_reporting`, `pipeline_reporting`, `revenue_reporting` |
| `repurpose` | `creative_asset_repurpose`, `social_posts_generator` |
| `research` | `company_deep_dive`, `person_research`, `personalization_research` |
| `research-plan` | `research_prioritization` |
| `reservations` | `reservation_handling` |
| `resources` | `resource_inventory_analyst` |
| `response` | `objection_response` |
| `response-sla` | `speed_to_lead` |
| `revenue` | `revenue_reporting` |
| `revenue-model` | `financial_business_planner` |
| `review` | `brand_voice_final_approvals` |
| `risk` | `risk_assessor`, `risk_committee` |
| `roadmap` | `product_roadmap_writer` |
| `roles` | `user_roles_permissions_writer` |
| `rollup` | `analytics_rollup` |
| `round` | `fundraising_strategist` |
| `routing` | `alert_routing`, `hot_lead_routing`, `trigger_detection` |
| `safety` | `incident_book` |
| `sam` | `market_study_by_country_analyst` |
| `save` | `save_calls` |
| `sbert` | `embeddings_provider` |
| `scaffolding` | `project_scaffolding` |
| `scaling` | `scaling_gate_definer` |
| `scheduling` | `meeting_booking` |
| `schema` | `data_schema_designer` |
| `scope` | `mvp_scoper`, `scope_calls`, `scope_change_control` |
| `scorecard` | `startup_valuation_analyst` |
| `scoring` | `fit_scoring` |
| `scrapegraphai` | `web_extraction` |
| `scraping` | `web_maps_scraping` |
| `screening` | `screening_scheduling` |
| `script` | `cold_call_scripting` |
| `sdr` | `cold_call_scripting` |
| `sec-edgar` | `fundamental_analyst` |
| `sector` | `vertical_analysis` |
| `segment-channel-message` | `validation_hypotheses_analyst` |
| `segmentation` | `lookalike_modeling`, `market_customer_profiler` |
| `self-serve` | `faq_self_serve` |
| `send-time` | `send_optimization` |
| `sensitivity` | `financial_excel_builder` |
| `seo` | `seo_briefs`, `validation_experiment_designer` |
| `sequences` | `cold_email_drafting` |
| `shared-inbox` | `inbox_triage` |
| `sidecar` | `framework_bridge`, `model_evaluation` |
| `signals` | `account_monitoring`, `health_scoring`, `reading_between_lines`, `social_mining`, `trigger_detection` |
| `sizing` | `risk_committee` |
| `skill` | `account_enrichment`, `contact_enrichment`, `data_visualization`, `document_extraction`, `email_verification`, `embeddings_provider`, … (+10) |
| `sla` | `hot_lead_routing` |
| `social` | `comment_cta_fulfillment`, `social_mining`, `social_night_recap`, `social_posts_generator` |
| `social-proof` | `proof_matching`, `ugc_pipeline` |
| `som` | `market_study_by_country_analyst` |
| `sop` | `sop_generation` |
| `sourcing` | `candidate_sourcing` |
| `sow` | `scope_calls` |
| `spec` | `integration_builds` |
| `speed` | `speed_to_lead` |
| `spend` | `spend_authority` |
| `spf` | `deliverability` |
| `sre` | `monitoring_alerting` |
| `stakeholders` | `network_mapping` |
| `states` | `ux_platform_designer` |
| `status` | `status_updates` |
| `strategic-accounts` | `key_account_relationships`, `strategic_account_calls`, `strategic_customer_accounts` |
| `strategy` | `deal_strategy_big_accounts` |
| `stt` | `voicebox_tts` |
| `summary` | `call_capture` |
| `swot` | `swot_analyst` |
| `sync` | `crm_sync`, `database_mining`, `portal_sync` |
| `synthesis` | `swot_analyst` |
| `tam` | `market_study_by_country_analyst`, `tam_market_sizing` |
| `targeting` | `icp_definition` |
| `teardown` | `competitor_teardown` |
| `tech-stack` | `minimal_tech_stack_cost_estimator`, `tech_stack_detection`, `tech_stack_vendors_analyst` |
| `technical` | `market_research_analyst` |
| `term-sheet` | `fundraising_strategist` |
| `terms` | `legal_ip_analyst` |
| `testing` | `model_evaluation` |
| `thesis` | `bull_bear_debate_pair` |
| `threshold` | `ltv_cac_targeter` |
| `throttle` | `send_optimization` |
| `ticket` | `ticket_triage` |
| `tiers` | `pricing_strategist` |
| `timesheets` | `timesheet_reconciliation` |
| `timing` | `market_trends_timing_analyst` |
| `together` | `llm_provider` |
| `tone` | `brand_identity_writer` |
| `trademark` | `legal_ip_analyst`, `legal_setup_cost_estimator` |
| `training` | `onboarding_training` |
| `tramo-0` | `legal_setup_cost_estimator`, `minimal_tech_stack_cost_estimator`, `tranche_0_budgeter` |
| `tramo-1` | `tranche_1_budgeter` |
| `transcript` | `transcript_processing` |
| `transcription` | `call_capture` |
| `treasury` | `banking_operations` |
| `trends` | `market_trends_timing_analyst` |
| `triage` | `email_triage_office`, `inbox_triage`, `ticket_triage` |
| `triggers` | `trigger_detection` |
| `trust` | `client_trust` |
| `tts` | `voicebox_tts` |
| `txtai` | `framework_bridge` |
| `ugc` | `ugc_pipeline` |
| `unit-economics` | `ltv_cac_targeter` |
| `upsell` | `expansion_playbook` |
| `usage` | `cost_usage_tracking` |
| `user-stories` | `functional_specifier` |
| `ux` | `ux_platform_designer` |
| `vad` | `local_inference` |
| `validation` | `validation_hypotheses_analyst` |
| `valuation` | `startup_valuation_analyst` |
| `vector-db` | `vector_store` |
| `vendors` | `tech_stack_vendors_analyst` |
| `verification` | `adversarial_verification`, `email_verification`, `qa_verification` |
| `vertical` | `vertical_analysis` |
| `video` | `video_prospecting` |
| `viz` | `data_visualization` |
| `voice` | `voicebox_tts` |
| `voicebox` | `voicebox_tts` |
| `voyage` | `embeddings_provider` |
| `warm-intro` | `warm_intro_pathing` |
| `warm-path` | `warm_path_finding` |
| `weaviate` | `vector_store` |
| `webgpu` | `local_inference` |
| `webinar` | `webinar_producer` |
| `weekly-update` | `status_updates` |
| `whisper` | `voicebox_tts` |
| `white-space` | `market_gap_analyst` |
| `win-loss` | `win_loss_analysis` |
| `xlsx` | `financial_excel_builder` |
| `zero-cost` | `resource_inventory_analyst` |
