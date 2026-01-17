"""
Predefined templates for common document types
"""
from .template_definitions import DocumentTemplate, TemplateSection, SectionType


# ============================================================================
# Template 1: 年度工作总结 (Annual Work Summary)
# ============================================================================
ANNUAL_WORK_SUMMARY = DocumentTemplate(
    id="annual_work_summary",
    name="年度工作总结",
    description="标准年度工作总结模板，包含工作成绩、经验反思、未来规划等部分",
    category="工作总结",
    sections=[
        TemplateSection(
            id="overview",
            title="一、开篇概览",
            section_type=SectionType.HEADING,
            word_count=100,
            requirements="简要总结年度工作总体情况，突出核心成果",
            placeholder_template="本年度，在[部门/团队]的领导下，围绕[核心目标]，主要完成了[重点工作领域]，取得了[关键成果]。"
        ),
        TemplateSection(
            id="achievements",
            title="二、主要成绩",
            section_type=SectionType.LIST,
            bullet_points=[
                "关键指标达成",
                "重点项目推进",
                "流程优化与降本增效",
                "客户/用户价值",
                "团队与人才培养",
                "创新与知识产权"
            ],
            subsections=[
                TemplateSection(
                    id="achievement_kpi",
                    title="• 关键指标达成",
                    section_type=SectionType.HEADING,
                    word_count=120,
                    requirements="量化描述关键指标的完成情况：营收、利润、用户数、交付率、成本节约等"
                ),
                TemplateSection(
                    id="achievement_projects",
                    title="• 重点项目推进",
                    section_type=SectionType.HEADING,
                    word_count=120,
                    requirements="项目名称+目标+结果（提前/超额/零事故），个人角色与贡献"
                ),
                TemplateSection(
                    id="achievement_optimization",
                    title="• 流程优化与降本增效",
                    section_type=SectionType.HEADING,
                    word_count=100,
                    requirements="引入的新工具、新流程、自动化脚本，节省人时/费用、缩短周期"
                ),
                TemplateSection(
                    id="achievement_customer",
                    title="• 客户/用户价值",
                    section_type=SectionType.HEADING,
                    word_count=100,
                    requirements="NPS、满意度、续约率、投诉下降，典型案例或表扬信"
                ),
                TemplateSection(
                    id="achievement_team",
                    title="• 团队与人才培养",
                    section_type=SectionType.HEADING,
                    word_count=100,
                    requirements="带教新人数量、晋升比例、培训场次、文化建设项目"
                ),
                TemplateSection(
                    id="achievement_innovation",
                    title="• 创新与知识产权",
                    section_type=SectionType.HEADING,
                    word_count=100,
                    requirements="专利/软著/论文/行业分享，内部创新大赛获奖"
                )
            ]
        ),
        TemplateSection(
            id="experience",
            title="三、经验与方法论",
            section_type=SectionType.HEADING,
            word_count=200,
            requirements="成功要素（目标拆解、数据驱动、跨部门协同），可复制模板（SOP、Checklist），个人成长（新技能、思维转变）"
        ),
        TemplateSection(
            id="problems",
            title="四、问题与反思",
            section_type=SectionType.LIST,
            bullet_points=["问题1", "问题2", "问题3"],
            subsections=[
                TemplateSection(
                    id="problem_1",
                    title="• 问题1",
                    section_type=SectionType.HEADING,
                    word_count=60,
                    requirements="目标偏差：未达成指标及根因（市场/资源/预判）"
                ),
                TemplateSection(
                    id="problem_2",
                    title="• 问题2",
                    section_type=SectionType.HEADING,
                    word_count=60,
                    requirements="过程痛点：需求频繁变更、沟通链路长、风险预警滞后"
                ),
                TemplateSection(
                    id="problem_3",
                    title="• 问题3",
                    section_type=SectionType.HEADING,
                    word_count=60,
                    requirements="能力短板：技术深度、行业洞察、时间管理、改进计划"
                )
            ]
        ),
        TemplateSection(
            id="next_year_goals",
            title="五、下一年度目标与策略",
            section_type=SectionType.HEADING,
            word_count=300,
            requirements="业务目标（营收增长、新客户占比）、能力目标（证书/技能）、团队目标（继任者覆盖率），策略与里程碑"
        ),
        TemplateSection(
            id="conclusion",
            title="六、结语",
            section_type=SectionType.HEADING,
            word_count=50,
            requirements="感谢领导与同事支持，表达持续贡献、共同成长的决心"
        ),
        TemplateSection(
            id="appendix",
            title="七、附录",
            section_type=SectionType.OPTIONAL,
            is_optional=True,
            requirements="可选：关键图表（收入曲线、项目甘特图、用户增长漏斗），链接（复盘PPT、数据仪表盘、知识库）"
        )
    ]
)


# ============================================================================
# Template 2: 项目总结报告 (Project Summary Report)
# ============================================================================
PROJECT_SUMMARY_REPORT = DocumentTemplate(
    id="project_summary_report",
    name="项目总结报告",
    description="项目完成后的总结报告模板，包含项目背景、成果、经验教训等",
    category="项目管理",
    sections=[
        TemplateSection(
            id="background",
            title="一、项目背景",
            section_type=SectionType.HEADING,
            word_count=150,
            requirements="项目启动的背景和原因，业务需求和目标"
        ),
        TemplateSection(
            id="objectives",
            title="二、项目目标与成果",
            section_type=SectionType.LIST,
            bullet_points=["目标1", "目标2", "目标3"],
            subsections=[
                TemplateSection(
                    id="objective_original",
                    title="• 原定目标",
                    section_type=SectionType.HEADING,
                    word_count=100,
                    requirements="项目启动时设定的目标和KPI"
                ),
                TemplateSection(
                    id="objective_actual",
                    title="• 实际成果",
                    section_type=SectionType.HEADING,
                    word_count=150,
                    requirements="最终达成的成果，与原定目标的对比，完成率"
                ),
                TemplateSection(
                    id="objective_highlight",
                    title="• 亮点成果",
                    section_type=SectionType.HEADING,
                    word_count=100,
                    requirements="超出预期的成果、创新点、获得的认可"
                )
            ]
        ),
        TemplateSection(
            id="implementation",
            title="三、实施过程",
            section_type=SectionType.HEADING,
            word_count=250,
            requirements="项目阶段划分、关键节点、时间线、团队协作方式"
        ),
        TemplateSection(
            id="challenges",
            title="四、遇到的挑战与解决方案",
            section_type=SectionType.LIST,
            bullet_points=["挑战1", "挑战2"],
            subsections=[
                TemplateSection(
                    id="challenge_1",
                    title="• 挑战1",
                    section_type=SectionType.HEADING,
                    word_count=100,
                    requirements="描述具体挑战，采取的解决方案，效果如何"
                ),
                TemplateSection(
                    id="challenge_2",
                    title="• 挑战2",
                    section_type=SectionType.HEADING,
                    word_count=100,
                    requirements="描述具体挑战，采取的解决方案，效果如何"
                )
            ]
        ),
        TemplateSection(
            id="lessons_learned",
            title="五、经验教训",
            section_type=SectionType.HEADING,
            word_count=200,
            requirements="做得好的方面（可复制）、需要改进的方面、下次避免的坑"
        ),
        TemplateSection(
            id="recommendations",
            title="六、后续建议",
            section_type=SectionType.HEADING,
            word_count=150,
            requirements="项目后续优化方向、二期规划、相关建议"
        ),
        TemplateSection(
            id="appendix",
            title="七、附录",
            section_type=SectionType.OPTIONAL,
            is_optional=True,
            requirements="项目文档、数据报表、相关链接"
        )
    ]
)


# ============================================================================
# Template 3: 会议纪要 (Meeting Minutes)
# ============================================================================
MEETING_MINUTES = DocumentTemplate(
    id="meeting_minutes",
    name="会议纪要",
    description="标准会议纪要模板，包含会议信息、讨论内容、决策事项、行动项等",
    category="会议管理",
    sections=[
        TemplateSection(
            id="basic_info",
            title="一、会议基本信息",
            section_type=SectionType.HEADING,
            word_count=100,
            requirements="会议时间、地点、参会人员、主持人、记录人"
        ),
        TemplateSection(
            id="topic",
            title="二、会议主题",
            section_type=SectionType.HEADING,
            word_count=80,
            requirements="本次会议的核心议题和会议目标"
        ),
        TemplateSection(
            id="agenda",
            title="三、议题讨论",
            section_type=SectionType.LIST,
            bullet_points=["议题1", "议题2", "议题3"],
            subsections=[
                TemplateSection(
                    id="agenda_1",
                    title="• 议题1",
                    section_type=SectionType.HEADING,
                    word_count=150,
                    requirements="议题背景、讨论过程、主要观点、结论"
                ),
                TemplateSection(
                    id="agenda_2",
                    title="• 议题2",
                    section_type=SectionType.HEADING,
                    word_count=150,
                    requirements="议题背景、讨论过程、主要观点、结论"
                ),
                TemplateSection(
                    id="agenda_3",
                    title="• 议题3",
                    section_type=SectionType.HEADING,
                    word_count=150,
                    requirements="议题背景、讨论过程、主要观点、结论"
                )
            ]
        ),
        TemplateSection(
            id="decisions",
            title="四、决策事项",
            section_type=SectionType.LIST,
            bullet_points=["决策1", "决策2"],
            subsections=[
                TemplateSection(
                    id="decision_1",
                    title="• 决策1",
                    section_type=SectionType.HEADING,
                    word_count=80,
                    requirements="决策内容、决策依据、执行要求"
                ),
                TemplateSection(
                    id="decision_2",
                    title="• 决策2",
                    section_type=SectionType.HEADING,
                    word_count=80,
                    requirements="决策内容、决策依据、执行要求"
                )
            ]
        ),
        TemplateSection(
            id="action_items",
            title="五、行动项",
            section_type=SectionType.HEADING,
            word_count=200,
            requirements="任务描述、负责人、截止时间、所需资源、依赖关系"
        ),
        TemplateSection(
            id="next_meeting",
            title="六、下次会议安排",
            section_type=SectionType.OPTIONAL,
            word_count=80,
            requirements="会议时间、地点、预期议题、需准备的材料"
        )
    ]
)


# ============================================================================
# Template 4: 工作计划 (Work Plan)
# ============================================================================
WORK_PLAN = DocumentTemplate(
    id="work_plan",
    name="工作计划",
    description="工作计划模板，包含目标、重点、具体安排、资源需求等",
    category="计划管理",
    sections=[
        TemplateSection(
            id="overview",
            title="一、目标概述",
            section_type=SectionType.HEADING,
            word_count=150,
            requirements="工作计划的总体目标、时间范围、预期成果"
        ),
        TemplateSection(
            id="priorities",
            title="二、工作重点",
            section_type=SectionType.LIST,
            bullet_points=["重点1", "重点2", "重点3"],
            subsections=[
                TemplateSection(
                    id="priority_1",
                    title="• 重点1",
                    section_type=SectionType.HEADING,
                    word_count=100,
                    requirements="重点工作内容、重要性说明"
                ),
                TemplateSection(
                    id="priority_2",
                    title="• 重点2",
                    section_type=SectionType.HEADING,
                    word_count=100,
                    requirements="重点工作内容、重要性说明"
                ),
                TemplateSection(
                    id="priority_3",
                    title="• 重点3",
                    section_type=SectionType.HEADING,
                    word_count=100,
                    requirements="重点工作内容、重要性说明"
                )
            ]
        ),
        TemplateSection(
            id="detailed_plan",
            title="三、具体计划",
            section_type=SectionType.LIST,
            bullet_points=["阶段1", "阶段2", "阶段3"],
            subsections=[
                TemplateSection(
                    id="phase_1",
                    title="• 阶段1",
                    section_type=SectionType.HEADING,
                    word_count=150,
                    requirements="时间周期、具体任务、交付物、负责人"
                ),
                TemplateSection(
                    id="phase_2",
                    title="• 阶段2",
                    section_type=SectionType.HEADING,
                    word_count=150,
                    requirements="时间周期、具体任务、交付物、负责人"
                ),
                TemplateSection(
                    id="phase_3",
                    title="• 阶段3",
                    section_type=SectionType.HEADING,
                    word_count=150,
                    requirements="时间周期、具体任务、交付物、负责人"
                )
            ]
        ),
        TemplateSection(
            id="resources",
            title="四、资源需求",
            section_type=SectionType.HEADING,
            word_count=150,
            requirements="人力、预算、设备、技术支持、外部协作等资源需求"
        ),
        TemplateSection(
            id="risks",
            title="五、风险评估",
            section_type=SectionType.LIST,
            bullet_points=["风险1", "风险2"],
            subsections=[
                TemplateSection(
                    id="risk_1",
                    title="• 风险1",
                    section_type=SectionType.HEADING,
                    word_count=80,
                    requirements="风险描述、可能性、影响程度、应对措施"
                ),
                TemplateSection(
                    id="risk_2",
                    title="• 风险2",
                    section_type=SectionType.HEADING,
                    word_count=80,
                    requirements="风险描述、可能性、影响程度、应对措施"
                )
            ]
        ),
        TemplateSection(
            id="metrics",
            title="六、考核指标",
            section_type=SectionType.HEADING,
            word_count=100,
            requirements="关键绩效指标（KPI）、完成标准、评估方式"
        )
    ]
)


# ============================================================================
# Template 5: 周报/月报 (Weekly/Monthly Report)
# ============================================================================
WEEKLY_MONTHLY_REPORT = DocumentTemplate(
    id="weekly_monthly_report",
    name="周报/月报",
    description="定期工作汇报模板，适用于周报、月报等周期性工作总结",
    category="工作汇报",
    sections=[
        TemplateSection(
            id="period_overview",
            title="一、本周/月工作概览",
            section_type=SectionType.HEADING,
            word_count=100,
            requirements="总体完成情况、工作亮点、简要评价"
        ),
        TemplateSection(
            id="completed_work",
            title="二、重点工作完成情况",
            section_type=SectionType.LIST,
            bullet_points=["工作1", "工作2", "工作3"],
            subsections=[
                TemplateSection(
                    id="work_1",
                    title="• 工作1",
                    section_type=SectionType.HEADING,
                    word_count=100,
                    requirements="工作内容、完成情况、产出成果、数据支撑"
                ),
                TemplateSection(
                    id="work_2",
                    title="• 工作2",
                    section_type=SectionType.HEADING,
                    word_count=100,
                    requirements="工作内容、完成情况、产出成果、数据支撑"
                ),
                TemplateSection(
                    id="work_3",
                    title="• 工作3",
                    section_type=SectionType.HEADING,
                    word_count=100,
                    requirements="工作内容、完成情况、产出成果、数据支撑"
                )
            ]
        ),
        TemplateSection(
            id="key_metrics",
            title="三、关键数据指标",
            section_type=SectionType.HEADING,
            word_count=100,
            requirements="核心业务指标完成情况、同比环比变化"
        ),
        TemplateSection(
            id="problems",
            title="四、遇到的问题",
            section_type=SectionType.HEADING,
            word_count=150,
            requirements="遇到的主要问题、阻碍因素、已采取的措施"
        ),
        TemplateSection(
            id="next_plan",
            title="五、下周/月工作计划",
            section_type=SectionType.LIST,
            bullet_points=["计划1", "计划2"],
            subsections=[
                TemplateSection(
                    id="next_1",
                    title="• 计划1",
                    section_type=SectionType.HEADING,
                    word_count=80,
                    requirements="重点工作、预期目标、时间安排"
                ),
                TemplateSection(
                    id="next_2",
                    title="• 计划2",
                    section_type=SectionType.HEADING,
                    word_count=80,
                    requirements="重点工作、预期目标、时间安排"
                )
            ]
        ),
        TemplateSection(
            id="support_needed",
            title="六、需要支持的事项",
            section_type=SectionType.OPTIONAL,
            word_count=100,
            requirements="需要协调的资源、需要支持的事项、建议"
        )
    ]
)


# ============================================================================
# Template 6: 调研报告 (Research Report)
# ============================================================================
RESEARCH_REPORT = DocumentTemplate(
    id="research_report",
    name="调研报告",
    description="市场/用户/产品调研报告模板",
    category="调研分析",
    sections=[
        TemplateSection(
            id="background",
            title="一、调研背景与目的",
            section_type=SectionType.HEADING,
            word_count=150,
            requirements="调研背景、调研目标、调研范围"
        ),
        TemplateSection(
            id="methodology",
            title="二、调研方法",
            section_type=SectionType.HEADING,
            word_count=120,
            requirements="调研方式（问卷/访谈/观察）、样本选择、数据收集方法"
        ),
        TemplateSection(
            id="findings",
            title="三、调研发现",
            section_type=SectionType.LIST,
            bullet_points=["发现1", "发现2", "发现3"],
            subsections=[
                TemplateSection(
                    id="finding_1",
                    title="• 发现1",
                    section_type=SectionType.HEADING,
                    word_count=150,
                    requirements="具体发现内容、数据支撑、案例说明"
                ),
                TemplateSection(
                    id="finding_2",
                    title="• 发现2",
                    section_type=SectionType.HEADING,
                    word_count=150,
                    requirements="具体发现内容、数据支撑、案例说明"
                ),
                TemplateSection(
                    id="finding_3",
                    title="• 发现3",
                    section_type=SectionType.HEADING,
                    word_count=150,
                    requirements="具体发现内容、数据支撑、案例说明"
                )
            ]
        ),
        TemplateSection(
            id="analysis",
            title="四、数据分析",
            section_type=SectionType.HEADING,
            word_count=200,
            requirements="关键数据分析、趋势分析、对比分析、可视化呈现"
        ),
        TemplateSection(
            id="conclusions",
            title="五、结论与建议",
            section_type=SectionType.HEADING,
            word_count=250,
            requirements="核心结论、具体建议、行动计划、后续研究方向"
        ),
        TemplateSection(
            id="appendix",
            title="六、附录",
            section_type=SectionType.OPTIONAL,
            is_optional=True,
            requirements="调研问卷、访谈记录、原始数据、参考资料"
        )
    ]
)


# ============================================================================
# Template 7: 问题分析报告 (Problem Analysis Report)
# ============================================================================
PROBLEM_ANALYSIS_REPORT = DocumentTemplate(
    id="problem_analysis_report",
    name="问题分析报告",
    description="问题根因分析及解决方案报告模板",
    category="问题管理",
    sections=[
        TemplateSection(
            id="description",
            title="一、问题描述",
            section_type=SectionType.HEADING,
            word_count=150,
            requirements="问题现象、发生时间、影响范围、严重程度"
        ),
        TemplateSection(
            id="analysis",
            title="二、问题分析（根因分析）",
            section_type=SectionType.HEADING,
            word_count=250,
            requirements="使用5Why、鱼骨图等工具进行根因分析，找出根本原因"
        ),
        TemplateSection(
            id="impact",
            title="三、影响评估",
            section_type=SectionType.LIST,
            bullet_points=["影响1", "影响2", "影响3"],
            subsections=[
                TemplateSection(
                    id="impact_1",
                    title="• 影响1",
                    section_type=SectionType.HEADING,
                    word_count=80,
                    requirements="受影响的方面、损失评估"
                ),
                TemplateSection(
                    id="impact_2",
                    title="• 影响2",
                    section_type=SectionType.HEADING,
                    word_count=80,
                    requirements="受影响的方面、损失评估"
                ),
                TemplateSection(
                    id="impact_3",
                    title="• 影响3",
                    section_type=SectionType.HEADING,
                    word_count=80,
                    requirements="受影响的方面、损失评估"
                )
            ]
        ),
        TemplateSection(
            id="solutions",
            title="四、解决方案",
            section_type=SectionType.LIST,
            bullet_points=["方案1", "方案2"],
            subsections=[
                TemplateSection(
                    id="solution_1",
                    title="• 方案1",
                    section_type=SectionType.HEADING,
                    word_count=150,
                    requirements="具体解决方案、实施步骤、所需资源、预期效果"
                ),
                TemplateSection(
                    id="solution_2",
                    title="• 方案2",
                    section_type=SectionType.HEADING,
                    word_count=150,
                    requirements="备选方案、适用条件、优劣势对比"
                )
            ]
        ),
        TemplateSection(
            id="prevention",
            title="五、预防措施",
            section_type=SectionType.HEADING,
            word_count=150,
            requirements="如何避免类似问题再次发生、流程改进、制度完善"
        ),
        TemplateSection(
            id="implementation",
            title="六、实施计划",
            section_type=SectionType.HEADING,
            word_count=150,
            requirements="实施时间表、责任人、验收标准、跟进机制"
        )
    ]
)


# ============================================================================
# Template 8: 培训总结 (Training Summary)
# ============================================================================
TRAINING_SUMMARY = DocumentTemplate(
    id="training_summary",
    name="培训总结",
    description="培训活动总结评估报告模板",
    category="培训管理",
    sections=[
        TemplateSection(
            id="basic_info",
            title="一、培训基本信息",
            section_type=SectionType.HEADING,
            word_count=100,
            requirements="培训名称、时间、地点、讲师、参训人员、培训时长"
        ),
        TemplateSection(
            id="objectives",
            title="二、培训目标",
            section_type=SectionType.HEADING,
            word_count=100,
            requirements="培训的总体目标、预期学习成果"
        ),
        TemplateSection(
            id="content",
            title="三、培训内容",
            section_type=SectionType.HEADING,
            word_count=150,
            requirements="培训的主要模块、核心知识点、培训方式（讲授/实操/讨论）"
        ),
        TemplateSection(
            id="feedback",
            title="四、学员反馈",
            section_type=SectionType.HEADING,
            word_count=200,
            requirements="满意度评分、正面反馈、改进建议、典型意见"
        ),
        TemplateSection(
            id="effectiveness",
            title="五、培训效果评估",
            section_type=SectionType.HEADING,
            word_count=200,
            requirements="知识掌握程度、技能提升情况、行为改变、工作绩效影响"
        ),
        TemplateSection(
            id="suggestions",
            title="六、改进建议",
            section_type=SectionType.HEADING,
            word_count=150,
            requirements="针对本次培训的改进建议、对未来培训的建议"
        )
    ]
)


# ============================================================================
# Template 9: 活动策划 (Event Planning)
# ============================================================================
EVENT_PLANNING = DocumentTemplate(
    id="event_planning",
    name="活动策划",
    description="活动/赛事策划方案模板",
    category="活动管理",
    sections=[
        TemplateSection(
            id="background",
            title="一、活动背景",
            section_type=SectionType.HEADING,
            word_count=120,
            requirements="活动举办的背景、目的和意义"
        ),
        TemplateSection(
            id="objectives",
            title="二、活动目标",
            section_type=SectionType.HEADING,
            word_count=100,
            requirements="具体目标、预期成果、成功标准"
        ),
        TemplateSection(
            id="theme",
            title="三、活动主题",
            section_type=SectionType.HEADING,
            word_count=80,
            requirements="活动主题、核心口号、宣传语"
        ),
        TemplateSection(
            id="audience",
            title="四、目标受众",
            section_type=SectionType.HEADING,
            word_count=100,
            requirements="目标人群分析、参与规模、覆盖范围"
        ),
        TemplateSection(
            id="agenda",
            title="五、活动流程",
            section_type=SectionType.LIST,
            bullet_points=["环节1", "环节2", "环节3"],
            subsections=[
                TemplateSection(
                    id="agenda_1",
                    title="• 环节1",
                    section_type=SectionType.HEADING,
                    word_count=100,
                    requirements="时间安排、活动内容、负责人"
                ),
                TemplateSection(
                    id="agenda_2",
                    title="• 环节2",
                    section_type=SectionType.HEADING,
                    word_count=100,
                    requirements="时间安排、活动内容、负责人"
                ),
                TemplateSection(
                    id="agenda_3",
                    title="• 环节3",
                    section_type=SectionType.HEADING,
                    word_count=100,
                    requirements="时间安排、活动内容、负责人"
                )
            ]
        ),
        TemplateSection(
            id="resources",
            title="六、资源需求",
            section_type=SectionType.HEADING,
            word_count=150,
            requirements="人力需求、物资设备、场地需求、预算估算"
        ),
        TemplateSection(
            id="risks",
            title="七、风险预案",
            section_type=SectionType.LIST,
            bullet_points=["风险1", "风险2"],
            subsections=[
                TemplateSection(
                    id="risk_1",
                    title="• 风险1",
                    section_type=SectionType.HEADING,
                    word_count=80,
                    requirements="可能的风险、应对措施、备选方案"
                ),
                TemplateSection(
                    id="risk_2",
                    title="• 风险2",
                    section_type=SectionType.HEADING,
                    word_count=80,
                    requirements="可能的风险、应对措施、备选方案"
                )
            ]
        ),
        TemplateSection(
            id="expected_outcome",
            title="八、预期效果",
            section_type=SectionType.HEADING,
            word_count=120,
            requirements="预期参与人数、媒体曝光、用户反馈、业务影响"
        )
    ]
)


# ============================================================================
# Template 10: 竞品分析 (Competitor Analysis)
# ============================================================================
COMPETITOR_ANALYSIS = DocumentTemplate(
    id="competitor_analysis",
    name="竞品分析",
    description="竞品分析报告模板",
    category="市场分析",
    sections=[
        TemplateSection(
            id="purpose",
            title="一、分析目的",
            section_type=SectionType.HEADING,
            word_count=100,
            requirements="本次竞品分析的目标、分析范围、应用场景"
        ),
        TemplateSection(
            id="overview",
            title="二、竞品概述",
            section_type=SectionType.LIST,
            bullet_points=["竞品A", "竞品B", "竞品C"],
            subsections=[
                TemplateSection(
                    id="competitor_a",
                    title="• 竞品A",
                    section_type=SectionType.HEADING,
                    word_count=120,
                    requirements="产品名称、公司背景、市场定位、用户规模"
                ),
                TemplateSection(
                    id="competitor_b",
                    title="• 竞品B",
                    section_type=SectionType.HEADING,
                    word_count=120,
                    requirements="产品名称、公司背景、市场定位、用户规模"
                ),
                TemplateSection(
                    id="competitor_c",
                    title="• 竞品C",
                    section_type=SectionType.HEADING,
                    word_count=120,
                    requirements="产品名称、公司背景、市场定位、用户规模"
                )
            ]
        ),
        TemplateSection(
            id="feature_comparison",
            title="三、功能对比",
            section_type=SectionType.HEADING,
            word_count=250,
            requirements="核心功能对比、差异化分析、优劣势对比（可用表格形式）"
        ),
        TemplateSection(
            id="strengths_weaknesses",
            title="四、优劣势分析",
            section_type=SectionType.LIST,
            bullet_points=["竞品A分析", "竞品B分析"],
            subsections=[
                TemplateSection(
                    id="swot_a",
                    title="• 竞品A分析",
                    section_type=SectionType.HEADING,
                    word_count=150,
                    requirements="优势（Strengths）、劣势（Weaknesses）、机会（Opportunities）、威胁（Threats）"
                ),
                TemplateSection(
                    id="swot_b",
                    title="• 竞品B分析",
                    section_type=SectionType.HEADING,
                    word_count=150,
                    requirements="优势（Strengths）、劣势（Weaknesses）、机会（Opportunities）、威胁（Threats）"
                )
            ]
        ),
        TemplateSection(
            id="market_positioning",
            title="五、市场定位",
            section_type=SectionType.HEADING,
            word_count=200,
            requirements="各竞品的市场定位、目标用户群、价格策略、推广策略"
        ),
        TemplateSection(
            id="insights",
            title="六、启示与建议",
            section_type=SectionType.HEADING,
            word_count=250,
            requirements="对产品的启示、改进方向、差异化策略、竞争策略建议"
        )
    ]
)


# ============================================================================
# Template Registry
# ============================================================================
PREDEFINED_TEMPLATES = {
    "annual_work_summary": ANNUAL_WORK_SUMMARY,
    "project_summary_report": PROJECT_SUMMARY_REPORT,
    "meeting_minutes": MEETING_MINUTES,
    "work_plan": WORK_PLAN,
    "weekly_monthly_report": WEEKLY_MONTHLY_REPORT,
    "research_report": RESEARCH_REPORT,
    "problem_analysis_report": PROBLEM_ANALYSIS_REPORT,
    "training_summary": TRAINING_SUMMARY,
    "event_planning": EVENT_PLANNING,
    "competitor_analysis": COMPETITOR_ANALYSIS,
}


def get_template(template_id: str):
    """
    Get a predefined template by ID

    Args:
        template_id: Template identifier

    Returns:
        DocumentTemplate object or None if not found
    """
    return PREDEFINED_TEMPLATES.get(template_id)


def list_all_templates():
    """
    List all predefined templates

    Returns:
        List of (template_id, template_name, template_category) tuples
    """
    return [
        (template_id, template.name, template.category)
        for template_id, template in PREDEFINED_TEMPLATES.items()
    ]


def list_templates_by_category(category: str):
    """
    List templates by category

    Args:
        category: Category name (e.g., "工作总结", "项目管理")

    Returns:
        List of matching templates
    """
    return [
        (template_id, template.name)
        for template_id, template in PREDEFINED_TEMPLATES.items()
        if template.category == category
    ]
