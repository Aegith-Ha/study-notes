# VS Code

## `__pycache__` 폴더 안 보이게 하기

`__pycache__`는 Python이 실행 중에 만드는 캐시 폴더다. 보통 직접 열거나 수정할 필요가 없다.

VS Code에서 안 보이게 하려면:

1. 명령 팔레트를 연다.
   - Windows/Linux: `Ctrl + Shift + P`
   - macOS: `Cmd + Shift + P`
2. `Preferences: Open User Settings (JSON)`을 선택한다.
3. 아래 설정을 추가한다.

```json
{
  "files.exclude": {
    "**/__pycache__": true
  }
}
```

이미 `files.exclude` 설정이 있다면, 그 안에 아래 한 줄만 추가한다.

```json
"**/__pycache__": true
```

## Git에서 Python 캐시 파일 제외하기

Python 캐시 파일이 Git에 올라가지 않도록 `.gitignore`에 아래 내용을 추가한다.

```gitignore
__pycache__/
*.py[cod]
```
