import { Result } from 'antd';
import React from 'react';

const NotAuthPage: React.FC = () => (
  <Result
    status="403"
    title="403"
    subTitle="你没有此页面的访问权限"
    extra={null}
  />
);

export default NotAuthPage;
