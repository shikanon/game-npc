import { defineConfig } from '@umijs/max';

export default defineConfig({
  antd: {
    appConfig: {
      message: {
        // 配置 message 最大显示数，超过限制时，最早的消息会被自动关闭
        maxCount: 3,
      },
    },
  },
  access: {},
  request: {
    dataField: 'data', // 配置请求响应时通过data消费数据
  },
  layout: false, // 禁用umi/max的默认layout布局
  model: {},
  initialState: {
    loading: '@/components/InitDataLoading',
  },
  clientLoader: {}, // 数据预加载
  codeSplitting: {
    // 代码拆分策略
    jsStrategy: 'granularChunks',
  },
  conventionRoutes: {
    // 不识别 components 和 models 目录下的文件为路由
    exclude: [/\/components\//, /\/models\//],
  },
  cssMinifierOptions: {
    // cssMinifier CSS 压缩工具配置选项
    minifyWhitespace: true,
    minifySyntax: true,
  },
  cssLoaderModules: {
    // 配置 css modules 的行为-驼峰式使用
    exportLocalsConvention: 'camelCase',
  },
  deadCode: {
    // 检测未使用的文件和导出，仅在 build 阶段开启
    detectUnusedFiles: true, // 是否检测未使用的文件
    detectUnusedExport: true, // 是否检测未使用的导出
  },
  esbuildMinifyIIFE: true, // 修复 esbuild 压缩器自动引入的全局变量导致的命名冲突问题
  favicons: [
    // 完整地址
    'http://management-game-npc.clarkchu.com/favicon.png',
    // 此时将指向 `/favicon.png` ，确保你的项目含有 `public/favicon.png`
    '/favicon.png',
  ], // 配置页面icon
  hash: true, // 开启 hash 模式，让 build 之后的产物包含 hash 后缀
  history: {
    type: 'hash',
  },
  inlineLimit: 10000, // 配置图片文件是否走 base64 编译的阈值
  jsMinifierOptions: {
    minifyWhitespace: true,
    minifyIdentifiers: true,
    minifySyntax: true,
  },
  metas: [
    // index页面meta描述
    { name: 'keywords', content: 'Game-NPC-管理后台' },
    { name: 'description', content: 'Game-NPC-管理后台' },
  ],
  mock: false, // 禁用mock数据
  publicPath: '/', // *** 普通环境项目部署到bsGW这种地址的时候，所有打包构建的资源要加一层path ***
  proxy: {
    // 开启本地代理功能
    '/local': {
      enable: true,
      changeOrigin: true,
      target: 'http://localhost:8080',
      pathRewrite: { '^/local': '/api' },
    },
    '/dev': {
      enable: true,
      changeOrigin: true,
      target: 'http://game-npc.clarkchu.com',
      pathRewrite: { '^/dev': '/api' },
    },
  },
  routes: [
    {
      path: '/',
      redirect: '/characterList',
    },
    {
      name: '角色管理',
      path: '/characterList',
      component: '@/pages/CharacterList',
    },
    {
      name: '角色配置',
      path: '/characterConfig',
      component: '@/pages/CharacterConfig',
    },
    {
      name: '调试NPC',
      path: '/chatDebug',
      component: '@/pages/ChatDebug',
      layout: false,
    },
    {
      name: ' 403',
      path: '/403',
      component: '@/pages/403',
    },
    {
      name: ' 404',
      path: '/*',
      component: '@/pages/404',
    },
  ],
  npmClient: 'pnpm', // 推荐使用pnpm
});
