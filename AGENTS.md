# 작업 규칙

## Phase 단위 실행 규칙

- 작업은 플랜 파일(`~/.claude/plans/claude-skills-browser-automation-skill-abundant-sphinx.md`)에 정의된 Phase 단위로 실행한다.
- **한 Phase가 완료되면 반드시 멈추고 사용자의 다음 지시를 기다린다.**
- 사용자가 명시적으로 "다음 phase로 넘어가줘" 또는 이에 준하는 지시를 하기 전까지 다음 Phase를 시작하지 않는다.
- 각 Phase 완료 후, 완료된 내용을 간략히 요약하고 다음 Phase에서 할 작업을 미리 안내한다.
