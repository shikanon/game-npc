import { useRequest } from 'ahooks';
import {
  Button, Modal,
  Spin,
  Typography,
} from 'antd';
import { ModalProps } from 'antd/es/modal';
import React, { useEffect, useState } from 'react';
import { ReloadOutlined } from "@ant-design/icons";
import npcService from "@/services/game_npc";
import { INPCInfo, NPCCharacterSexEnum } from "@/interfaces/game_npc";
import { useModel } from "@@/exports";

const { Text, Paragraph } = Typography;

interface Values {
  npcInfo: INPCInfo | null;
  shortDescription: string;
  onChange: (values: any) => void;
}

const CreateFormModal: React.FC<Values & ModalProps> = ({
  npcInfo,
  shortDescription,
  onChange,
  ...modalProps
}) => {
  const { setOpenPromptModal } = useModel('user');

  const [prompt, setPrompt] = useState<string|null>(null);

  const { runAsync: generatorNpcTraitRequest, loading: generatorNpcTraitLoading } =
    useRequest(npcService.GeneratorNpcTrait, { manual: true });

  /**
   * 生成角色描述
   */
  const generatorNpcTrait = async () => {
    const result = await generatorNpcTraitRequest({
      npcName: npcInfo?.name || '',
      npcSex: npcInfo?.sex === NPCCharacterSexEnum.NPCCharacterSexEnum_Male ? '男' : '女',
      npcShortDescription: shortDescription,
    });
    console.log(result, '生成结果');
    if (result?.data) {
      setPrompt(result.data);
    }
  }

  useEffect(() => {
    if (modalProps.open) {
      generatorNpcTrait().then()
    }
  }, [modalProps.open]);

  return (
    <Modal
      {...modalProps}
      title={(
        <Paragraph>生成角色描述<br/><Text style={{ color: '#8c8c8c' }}>根据角色姓名、性别、简短描述生成角色描述</Text></Paragraph>
      )}
      okText={null}
      cancelText={null}
      width={450}
      styles={{
        body: { padding: '10px 0px 0 0px' },
      }}
      closeIcon={(
        <ReloadOutlined style={{ color: '#EB2F96' }} />
      )}
      onCancel={() => {
        generatorNpcTrait().then();
      }}
      onOk={() => {

      }}
      footer={[
        <Button
          key={1}
          onClick={() => {
            setOpenPromptModal(false);
          }}
        >
          取消
        </Button>,
        <Button
          key={2}
          type={'primary'}
          style={{ backgroundColor: '#EB2F96' }}
          onClick={() => {
            onChange(prompt);
            setOpenPromptModal(false);
            setPrompt(null);
          }}
        >
          使用
        </Button>,
      ]}
    >
      <Spin spinning={generatorNpcTraitLoading}>
        <div style={{ minHeight: 100 }}>{prompt}</div>
      </Spin>
    </Modal>
  );
};

export default CreateFormModal;
