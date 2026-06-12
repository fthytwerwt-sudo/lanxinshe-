# Codex 工作区与远端仓库硬边界

## 文件定位

本文件规定当前项目中 Codex 的本地工作区和远端上传边界。

本文件只承载执行安全边界，不承载项目事实。

## 本地工作区硬约束

Codex 在当前项目中只能在用户授权的 workspace（当前工作目录 / 工作区）内工作。

默认禁止：

- 在授权 workspace 外新建工作区。
- 在授权 workspace 外新建项目目录、报告目录、脚本目录、临时产物目录。
- 在桌面、Downloads、Documents 根目录、其他项目目录中生成当前项目产物。
- 未经授权另行 clone 当前仓库到其他路径。
- 未经授权读取或修改其他项目目录。

执行前必须检查：

```text
pwd
git rev-parse --show-toplevel
```

如果当前路径不在用户本轮授权 workspace 内，必须停止并标：

```text
blocked_wrong_workspace
```

## 远端仓库硬约束

当前项目唯一允许写入 / push（推送）的 GitHub 仓库必须来自用户本轮明确授权。

默认禁止：

- push 到其他 GitHub 仓库。
- commit 到其他项目仓库。
- 创建指向其他仓库的 PR。
- 上传当前项目文件到其他仓库。
- 把当前项目事实写入旧项目仓库。
- 把旧项目仓库当成当前项目远端。

执行前必须检查：

```text
git remote -v
git branch --show-current
```

如果 remote（Git 远端仓库地址）不指向用户本轮授权仓库，必须停止并标：

```text
blocked_existing_wrong_remote
```

## 允许的例外

只有用户本轮明确授权时，才可以：

- 在授权的其他路径读取文件。
- 在授权的其他路径生成临时文件。
- 只读参考其他仓库。
- 上传到其他指定仓库。

授权必须来自用户本轮明确输入，不能来自历史聊天、旧项目经验或 Codex 自行判断。

即使获得只读参考授权，也不得对其他仓库执行 commit / push，除非用户明确说允许写入该仓库。

## Codex 执行口径

先确认工作区，再确认远端；路径不对不动文件，remote 不对不 push。

## 一句话执行口径

Codex 只能在授权 workspace 内干活，只能把当前项目改动 push 到用户本轮授权 remote；越界就 blocked。
