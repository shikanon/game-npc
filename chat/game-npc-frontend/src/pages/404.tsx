import { Button, Result } from 'antd';
import React from 'react';
import { history } from '@umijs/max';

const NotFoundPage: React.FC = () => (
  <Result
    status="404"
    title="404"
    subTitle="你访问的页面不存在"
    extra={
      <Button type="primary" onClick={() => history?.push('/')}>
        返回
      </Button>
    }
  />
);

export default NotFoundPage;
