import dayjs from 'dayjs';
import { v4 as uuidv4 } from 'uuid';

/**
 * 生成带有前缀的UUID
 * @param prefix 前缀字符串，可选
 * @returns 返回生成的UUID字符串
 */
export function generatePrefixedUUID(prefix?: string): string {
  // 使用UUID生成器生成真正的UUID
  const uuid = uuidv4();
  if (!prefix) {
    return uuid;
  }

  // 标准化前缀
  const normalizedPrefix = prefix
    .trim()
    .replace(/[^a-z0-9_-]/gi, '')
    .replace(/[_-]+/g, '-');
  return `${normalizedPrefix}-${uuid}`;
}

/**
 * 将时间戳格式化为指定格式的日期字符串
 * @param timestamp 时间戳
 * @param format 时间格式，可选，默认为 'YYYY-MM-DD HH:mm:ss'
 * @returns 返回格式化后的日期字符串，如果时间戳无效，则返回 null
 */
export function formatTimestamp(
  timestamp: number | string | Date | undefined,
  format = 'YYYY-MM-DD HH:mm:ss',
): string | null {
  if (!timestamp) {
    return null;
  }
  try {
    const res = dayjs(timestamp);
    return res.format(format);
  } catch (error) {
    console.error(`Invalid timestamp: ${timestamp}`, error);
    return null;
  }
}

/**
 * 修改url参数
 * @param paramKey
 * @param paramValue
 */
export const modifyParamInHashURL = (paramKey: string, paramValue: string) => {
  const url = new URL(window.location.href);
  let [hashPath, hashQuery = ''] = url.hash.split('?');
  const hashUrl = new URL(`?${hashQuery}`, url.href);

  if (hashUrl.searchParams.has(paramKey)) {
    hashUrl.searchParams.set(paramKey, paramValue);
  } else {
    // 这里如果发现paramKey不存在，可以根据需要决定是否要报错或直接添加参数
    hashUrl.searchParams.append(paramKey, paramValue);
  }

  const newQuery = hashUrl.searchParams.toString();
  url.hash = newQuery ? `${hashPath}?${newQuery}` : hashPath;

  // 更新URL，但不会引起页面刷新
  history.replaceState(null, document.title, url.toString());
};

/**
 * 删除url参数
 * @param paramKey
 */
export const removeParamFromHashURL = (paramKey: string = '') => {
  const url = new URL(window.location.href);
  let [hashPath, hashQuery = ''] = url.hash.split('?');
  const hashUrl = new URL(`?${hashQuery}`, url.href);

  if (hashUrl.searchParams.has(paramKey)) {
    hashUrl.searchParams.delete(paramKey);
  } else {
    // 删除所有参数
    for (const key of hashUrl.searchParams.keys()) {
      hashUrl.searchParams.delete(key);
    }
  }

  // 判断查询参数是否为空，否则不添加 "?"
  const newQuery = hashUrl.searchParams.toString();
  url.hash = newQuery ? `${hashPath}?${newQuery}` : hashPath;

  // 更新URL，但不会引起页面刷新
  history.replaceState(null, document.title, url.toString());
};

/**
 * 获取随机颜色
 */
export function getRandomColor(index: number) {
  const colorsList = [
    '#6596FA',
    '#63DAAB',
    '#ffec3d',
    '#13c2c2',
    '#FCEB60',
    '#9254de',
    'orange',
    'gold',
    'lime',
    'green',
    'cyan',
    'blue',
    'purple',
  ];
  const i = index % colorsList.length; // 数组下标循环使用
  return colorsList[i];
}

/**
 * 获取url参数
 */
export function getHashParams() {
  const hash = window.location.hash;
  const queryString = hash.split('?')[1];
  if (!queryString) return {};

  const paramPairs = queryString.split('&');
  const params: { [key: string]: string } = {}; // 声明 params 是一个具有字符串索引签名的对象

  paramPairs.forEach((pair) => {
    const [key, value] = pair.split('=');
    params[key] = decodeURIComponent(value);
  });

  return params;
}
