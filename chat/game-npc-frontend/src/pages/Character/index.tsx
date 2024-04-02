import chatTipsImg from '@/assets/images/chat_tips.png';
import { INPCInfo } from '@/interfaces/game_npc';
import gameNpcService from '@/services/game_npc';
import { history } from '@umijs/max';
import { useMount, useRequest } from 'ahooks';
import { Col, Image, Row, Typography } from 'antd';
import { useTheme } from 'antd-style';
import { useEffect, useState } from 'react';
import styles from './index.less';

const { Paragraph } = Typography;

const Character = () => {
  const theme = useTheme();
  const [characterList, setCharacterList] = useState<INPCInfo[]>([]);

  // 获取NPC角色列表
  const { loading: getNPCListLoading, runAsync: getNPCListRequest } =
    useRequest(gameNpcService.GetNPCList, { manual: true });

  /**
   * 获取NPC角色列表
   */
  const getNPCList = async () => {
    const result = await getNPCListRequest({
      page: 1,
      limit: 10,
    });
    console.log('result', result);
    if (result?.data?.list.length) {
      setCharacterList(result.data.list);
    } else {
      setCharacterList([]);
    }
  };

  useMount(() => {
    getNPCList().then();
  });

  useEffect(() => {}, []);

  return (
    <div
      style={{
        backgroundColor: theme.colorBgLayout,
      }}
      className={styles.container}
    >
      {/*<div className={styles.background}>*/}
      {/*  <div></div>*/}
      {/*  <div></div>*/}
      {/*  <div></div>*/}
      {/*</div>*/}

      <div className={styles.characterContainer}>
        {/*<Row justify={'center'} className={styles.title}>*/}
        {/*  <Image preview={false} src={chatTipsImg} height={50} />*/}
        {/*</Row>*/}

        <Row gutter={36} style={{ marginTop: 40 }} wrap={true}>
          {characterList.map((item) => {
            return (
              <Col key={item.id}>
                <Row justify={'center'}>
                  <div
                    className={styles.characterItem}
                    style={{
                      backgroundImage: `url(${item?.chatBackground})`,
                    }}
                    onClick={() => {
                      history.push(`/conversation?characterId=${item.id}`);
                    }}
                  >
                    <Col className={styles.characterAttr}>
                      <Row justify={'center'} className={styles.name}>
                        {item?.name || '-'}
                      </Row>
                      {
                        item?.shortDescription ? (
                          <Row>
                            <Paragraph
                              className={styles.desc}
                            >
                              {item?.shortDescription || '-'}
                            </Paragraph>
                          </Row>
                        ) : null
                      }
                    </Col>
                  </div>
                </Row>
              </Col>
            );
          })}
        </Row>
      </div>
    </div>
  );
};

export default Character;
