import { generatePrefixedUUID } from '@/utils';
import { useBoolean } from 'ahooks';
import { message } from 'antd';
import { DrawerProps } from 'antd/es/drawer';
import React, { useEffect, useState } from 'react';

interface IProps {
  drawer: React.ReactElement<DrawerProps>;
  children: React.ReactNode;
  closeTrigger?: string;
  destroyOnClose?: boolean;
  forceRender?: boolean;
}

export const DrawerPanel: React.FC<IProps> = ({
  drawer,
  children,
  closeTrigger = 'onClose',
  destroyOnClose = false,
  forceRender = false,
}) => {
  const [open, { setTrue: setVisible, setFalse: setInvisible }] =
    useBoolean(false);
  const [drawerKey, setDrawerKey] = useState(generatePrefixedUUID('drawer-'));
  const [messageApi] = message.useMessage();

  useEffect(() => {
    if (open && destroyOnClose) {
      setDrawerKey(generatePrefixedUUID('drawer-'));
    }
  }, [open, destroyOnClose]);

  return (
    <>
      {React.Children.map(children, (child) => {
        if (React.isValidElement(child)) {
          return React.cloneElement(child, {
            ...child.props,
            onClick: async (
              e: React.MouseEvent<HTMLElement, MouseEvent>,
            ): Promise<void> => {
              try {
                if (child.props?.onClick) {
                  await child.props.onClick(e);
                }
                setVisible();
              } catch (error) {
                if (typeof error === 'string') {
                  messageApi.warning(error);
                } else if (error instanceof Error) {
                  messageApi.warning(error.message);
                }
              }
            },
          });
        } else {
          return child;
        }
      })}
      {React.cloneElement(drawer, {
        key: drawerKey,
        open,
        destroyOnClose,
        forceRender,
        [closeTrigger]: async (...args: unknown[]) => {
          // @ts-ignore
          if (drawer.props[closeTrigger] instanceof Function) {
            // @ts-ignore
            await drawer.props[closeTrigger](...args);
          }
          setInvisible();
        },
      })}
    </>
  );
};

DrawerPanel.defaultProps = {
  closeTrigger: 'onClose',
  destroyOnClose: false,
  forceRender: false,
};

export default DrawerPanel;
