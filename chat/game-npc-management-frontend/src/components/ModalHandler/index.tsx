// 通用弹窗
import { generatePrefixedUUID } from '@/utils';
import { useBoolean } from 'ahooks';
import { message } from 'antd';
import { ModalProps } from 'antd/es/modal';
import React from 'react';

interface IProps {
  modal: React.ReactElement<ModalProps>;
  children: React.ReactNode;
  onClick?: (event: React.MouseEvent) => Promise<void>;
  okTrigger?: string;
  invisibleTrigger?: string;
  destroyOnClose?: boolean;
  forceRender?: boolean;
}

export const ModalHandler: React.FC<IProps> = ({
  modal,
  children,
  onClick,
  okTrigger = 'onOk',
  invisibleTrigger = 'onCancel',
  destroyOnClose = false,
  forceRender = false,
}) => {
  const [open, { setTrue: setVisible, setFalse: setInvisible }] =
    useBoolean(false);
  const [messageApi] = message.useMessage();

  return (
    <>
      {React.Children.map(children, (child) => {
        if (React.isValidElement(child)) {
          return React.cloneElement(child, {
            ...child.props,
            onClick: async (
              e: React.MouseEvent<HTMLElement, MouseEvent>,
            ): Promise<void> => {
              let showModal = true;
              try {
                if (child.props?.onClick) {
                  showModal = await child.props.onClick(e);
                }
                if (showModal) {
                  setVisible();
                }
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
      {React.cloneElement(modal, {
        key: generatePrefixedUUID('modal-'),
        open: open,
        destroyOnClose,
        forceRender,
        [okTrigger]: async (...args: unknown[]) => {
          // @ts-ignore
          if (modal.props[okTrigger] instanceof Function) {
            // @ts-ignore
            await modal.props[okTrigger](...args);
          }
          setInvisible();
        },
        [invisibleTrigger]: (...args: unknown[]) => {
          setInvisible();
          // @ts-ignore
          if (modal.props[invisibleTrigger] instanceof Function) {
            // @ts-ignore
            modal.props[invisibleTrigger](...args);
          }
        },
      })}
    </>
  );
};

ModalHandler.defaultProps = {
  okTrigger: 'onOk',
  invisibleTrigger: 'onCancel',
  destroyOnClose: false,
  forceRender: false,
};

export default ModalHandler;
