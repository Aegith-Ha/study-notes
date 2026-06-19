## File Encoding Rules

# project
이 프로젝트는 학습기록용 프로젝트다.

# for korean
- 한글이 포함된 `.jsp`, `.xml`, `.properties`, `.java`, `.js`, `.css` 파일은 `apply_patch`로만 수정한다.
- `shell_command`를 사용한 직접 파일 쓰기(`Set-Content`, `Out-File`, `>`, `>>`)로 한글 포함 파일을 덮어쓰지 않는다.
- 부득이하게 쉘로 파일을 써야 하면 반드시 UTF-8 인코딩을 명시하고, 수정 직후 깨진 문자열이 없는지 확인하고 알려준다.
- 모든 응답은 한국어로 작성 한다.

# for prevent remove
- 수정해줘, 생성해줘 같이 직접적으로 소스를 변경하는 지시를 하지 않으면 소스를 수정하거나 생성하지 않고 설명만 한다.

# git
- git push, commit 은 하지 않는다.