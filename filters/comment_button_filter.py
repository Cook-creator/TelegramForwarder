import logging
import asyncio
from telethon import Button
from filters.base_filter import BaseFilter
from telethon.tl.functions.channels import GetFullChannelRequest
from utils.common import get_main_module

logger = logging.getLogger(__name__)

class CommentButtonFilter(BaseFilter):
    """
    评论区按钮过滤器，用于在消息中添加指向关联群组消息的按钮
    """
    
    async def _process(self, context):
        """
        为消息添加评论区按钮
        
        Args:
            context: 消息上下文
            
        Returns:
            bool: 是否继续处理
        """
        # 如果规则不存在或未启用评论按钮功能，直接跳过
        if not context.rule or not context.rule.enable_comment_button:
            return True
            
        # 如果消息内容为空，直接跳过
        if not context.original_message_text and not context.event.message.media:
            return True
            
        try:
            # 获取用户客户端而不是Bot客户端
            main = await get_main_module()
            client = main.user_client if (main and hasattr(main, 'user_client')) else context.client
            
            event = context.event
            
            # 获取原始频道实体
            channel_entity = await client.get_entity(event.chat_id)
            
            # 只处理频道消息
            if not hasattr(channel_entity, 'broadcast') or not channel_entity.broadcast:
                return True
                
            # 获取关联群组ID
            try:
                # 获取频道完整信息
                full_channel = await client(GetFullChannelRequest(channel_entity))
                
                # 检查是否有关联群组
                if not full_channel.full_chat.linked_chat_id:
                    logger.info(f"频道 {channel_entity.id} 没有关联群组，跳过添加评论按钮")
                    return True
                    
                linked_group_id = full_channel.full_chat.linked_chat_id
                
                # 获取关联群组实体
                linked_group = await client.get_entity(linked_group_id)
                
                # 获取频道消息ID
                channel_msg_id = event.message.id
                
                # 添加短暂延迟，等待消息同步完成
                logger.info("等待1秒，确保消息同步完成...")
                await asyncio.sleep(1)
                
                # 构建评论区链接 - 不依赖于匹配群组消息
                if hasattr(channel_entity, 'username') and channel_entity.username:
                    # 直接构建带comment=1的链接，这会打开频道消息并自动显示评论区
                    # 虽然可能不会精确滚动到匹配消息，但至少能打开评论区
                    comment_link = f"https://t.me/{channel_entity.username}/{channel_msg_id}?comment=1"
                    logger.info(f"构建基本评论区链接: {comment_link}")
                    
                    # 如果可以获取群组消息，尝试找到精确匹配以提供更好的体验
                    try:
                        # 查找关联群组中对应的消息 - 使用用户客户端
                        logger.info(f"尝试使用用户客户端获取群组 {linked_group_id} 的消息")
                        group_messages = await client.get_messages(linked_group, limit=5)
                        logger.info(f"成功获取关联群组 {linked_group_id} 的 {len(group_messages)} 条消息")
                        
                        # 尝试查找内容相同的消息
                        matched_msg = None
                        
                        # 1. 先尝试完全匹配内容
                        original_message = context.original_message_text
                        if original_message:
                            logger.info(f"尝试查找内容完全匹配的消息，原始内容长度: {len(original_message)}")
                            
                            for msg in group_messages:
                                if hasattr(msg, 'message') and msg.message and msg.message == original_message:
                                    matched_msg = msg
                                    logger.info(f"找到完全匹配消息: 群组消息ID {msg.id}")
                                    break
                        
                        # 2. 如果无法完全匹配，尝试部分匹配
                        if not matched_msg and original_message and len(original_message) > 20:
                            # 使用消息前20个字符作为特征
                            message_start = original_message[:20]
                            logger.info(f"尝试部分匹配，使用消息前20个字符: '{message_start}'")
                            
                            for msg in group_messages:
                                if hasattr(msg, 'message') and msg.message and message_start in msg.message:
                                    matched_msg = msg
                                    logger.info(f"找到部分匹配消息: 群组消息ID {msg.id}")
                                    break
                        
                        # 3. 如果没找到匹配消息，尝试基于时间匹配
                        if not matched_msg and hasattr(event.message, 'date'):
                            message_time = event.message.date
                            logger.info(f"尝试基于时间匹配，原消息时间: {message_time}")
                            
                            # 获取消息时间前后10分钟内的消息
                            time_window = 10  # 分钟
                            
                            for msg in group_messages:
                                if hasattr(msg, 'date'):
                                    time_diff = abs((msg.date - message_time).total_seconds())
                                    if time_diff < time_window * 60:
                                        matched_msg = msg
                                        logger.info(f"找到时间接近的消息: 群组消息ID {msg.id}, 时间差: {time_diff}秒")
                                        break
                        
                        # 4. 如果仍未找到，使用最新消息
                        if not matched_msg:
                            logger.info("未找到匹配消息，尝试使用最新消息")
                            # 使用最新消息作为默认值
                            if group_messages:
                                matched_msg = group_messages[0]
                                logger.info(f"使用最新消息: 群组消息ID {matched_msg.id}")
                        
                        # 如果找到了匹配消息，更新链接
                        if matched_msg:
                            group_msg_id = matched_msg.id
                            comment_link = f"https://t.me/{channel_entity.username}/{channel_msg_id}?comment={group_msg_id}"
                            logger.info(f"更新为精确评论区链接: {comment_link}")
                        
                    except Exception as e:
                        logger.warning(f"获取群组消息失败，可能是因为未加入群组: {str(e)}")
                        logger.info("将使用基本评论区链接")
                        # 保持使用基本的comment=1链接
                else:
                    # 如果频道没有用户名，则无法构建评论区链接
                    logger.warning(f"频道 {channel_entity.id} 没有用户名，无法构建评论区链接")
                    # 尝试使用直接链接到群组
                    if hasattr(linked_group, 'username') and linked_group.username:
                        comment_link = f"https://t.me/{linked_group.username}"
                        logger.info(f"生成群组链接: {comment_link}")
                    else:
                        comment_link = None
                        logger.warning("无法生成评论区或群组链接")
                
                if comment_link:
                    # 创建评论区按钮
                    comment_button = Button.url("💬 查看评论区", comment_link)
                    
                    # 将按钮添加到消息中
                    if not context.buttons:
                        context.buttons = [[comment_button]]
                    else:
                        # 如果已经有按钮，添加到第一行
                        context.buttons.insert(0, [comment_button])
                    
                    logger.info(f"为消息添加了评论区按钮，链接: {comment_link}")
                    
                    # # 如果有私有群组或用户未加入群组，考虑添加加入群组按钮
                    # if hasattr(linked_group, 'username') and linked_group.username:
                    #     join_link = f"https://t.me/{linked_group.username}"
                    #     join_button = Button.url("➕ 加入讨论群组", join_link)
                        
                    #     # 添加加入群组按钮
                    #     if not context.buttons:
                    #         context.buttons = [[join_button]]
                    #     else:
                    #         # 尝试添加到第一行或第二行
                    #         if len(context.buttons) > 0 and len(context.buttons[0]) < 2:
                    #             context.buttons[0].append(join_button)
                    #         else:
                    #             context.buttons.insert(1, [join_button])
                                
                    #     logger.info(f"添加了加入群组按钮，链接: {join_link}")
            except Exception as e:
                logger.error(f"获取关联群组消息时出错: {str(e)}")
                import traceback
                logger.error(traceback.format_exc())
                
        except Exception as e:
            logger.error(f"添加评论区按钮时出错: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            
        return True 