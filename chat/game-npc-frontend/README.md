# GAME-NPC Project

GAME-NPC项目

# Umi 4 + React 18 + TypeScript 5 + AntD 5

```bash
# 安装依赖
$ pnpm install

# 启动服务
$ pnpm dev         # 开发 http://localhost:8000
$ pnpm proto       # proto协议转TypeScript类型声明
$ pnpm build       # 项目打包构建
```

[Umi脚手架更多介绍](https://umijs.org/docs/introduce/introduce)

## 目录

```md
.
├── dist                             // 打包构建产物
├── mock                             // Mock文件
│   └── user.ts | tsx                // mock接口
├── src                              // 项目代码资源
│   ├── .umi                         // dev 时的临时文件目录
│   ├── .umi-production              // build 时的临时文件目录
│   ├── interfaces                   // api接口类型定义目录
│   │   └── api.ts
│   ├── models                       // 数据model
│   │   ├── global.ts                // 全局信息相关状态
│   │   └── user.ts                  // 用户信息相关状态
│   ├── pages                        // 页面
│   │   ├── index.less
│   │   └── index.tsx
│   ├── utils                        // 工具文件
│   │   └── index.ts
│   ├── services                     // api接口目录
│   │   └── api.ts
│   ├── app.(ts|tsx)                      // 项目运行时配置 入口文件
│   ├── global.ts                         // 全局前置脚本文件
│   ├── global.(css|less|sass|scss)       // 全局样式文件
│   ├── overrides.(css|less|sass|scss)    // 高优先级全局样式文件
│   ├── favicon.(ico|gif|png|jpg|svg...)  // 站点 favicon 图标文件
│   └── loading.(tsx|jsx)                 // 全局加载组件
├── node_modules
│   └── .cache
│       ├── bundler-webpack
│       ├── mfsu
│       └── mfsu-deps
├── .env                                  // 环境变量
├── plugin.ts                             // 项目级 Umi 插件
├── .umirc.ts                             // 配置文件，包含 Umi 所有非运行时配置
├── package.json
├── tsconfig.json
└── typings.d.ts
```
