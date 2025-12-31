import React, { useState, useRef, useEffect } from 'react';
import {
  View,
  StyleSheet,
  FlatList,
  TextInput,
  KeyboardAvoidingView,
  Platform,
  TouchableOpacity,
} from 'react-native';
import {
  Text,
  Avatar,
  IconButton,
  Surface,
  ActivityIndicator,
} from 'react-native-paper';
import { useSelector } from 'react-redux';
import { RootState } from '../../store/store';
import { CHAT_MESSAGES, MOCK_USERS } from '../../services/mockData';
import { getRelativeTime } from '../../utils/helpers';
import { COLORS } from '../../theme';

type Message = typeof CHAT_MESSAGES[0];

export default function ChatScreen() {
  const { user } = useSelector((state: RootState) => state.auth);
  const [messages, setMessages] = useState<Message[]>(CHAT_MESSAGES);
  const [messageInput, setMessageInput] = useState('');
  const [isSending, setIsSending] = useState(false);
  const flatListRef = useRef<FlatList>(null);

  // Mock contacts based on user role
  const getContacts = () => {
    if (!user) return [];

    const contacts = [];
    contacts.push({
      id: 'teacher-001',
      name: 'Mr. Rahul Sharma',
      role: 'Mathematics Teacher',
      lastMessage: 'Please check the homework',
      time: '10:30 AM',
      unread: 2,
      avatar: 'RS',
    });
    contacts.push({
      id: 'admin-001',
      name: 'School Admin',
      role: 'Administration',
      lastMessage: 'Fee notice has been sent',
      time: 'Yesterday',
      unread: 0,
      avatar: 'SA',
    });
    contacts.push({
      id: 'parent-001',
      name: 'Sanjay Kumar',
      role: 'Parent',
      lastMessage: 'Thank you for the update',
      time: 'Yesterday',
      unread: 0,
      avatar: 'SK',
    });
    return contacts;
  };

  const [contacts] = useState(getContacts());
  const [selectedContact, setSelectedContact] = useState(contacts[0]);

  const handleSend = async () => {
    if (!messageInput.trim()) return;

    setIsSending(true);

    // Simulate sending message
    await new Promise((resolve) => setTimeout(resolve, 500));

    const newMessage: Message = {
      id: Date.now().toString(),
      senderId: user?.id || 'user-001',
      receiverId: selectedContact.id,
      message: messageInput,
      timestamp: new Date().toISOString(),
      type: 'sent',
    };

    setMessages([...messages, newMessage]);
    setMessageInput('');
    setIsSending(false);

    // Scroll to bottom
    setTimeout(() => {
      flatListRef.current?.scrollToEnd({ animated: true });
    }, 100);
  };

  const renderMessageItem = ({ item }: { item: Message }) => {
    const isSent = item.senderId === user?.id;
    const isSelectedContact = item.receiverId === selectedContact.id;

    return (
      <View
        style={[
          styles.messageContainer,
          isSent ? styles.sentMessage : styles.receivedMessage,
        ]}
      >
        {!isSent && (
          <Avatar.Text
            size={28}
            label={selectedContact.avatar}
            style={styles.messageAvatar}
          />
        )}
        <View
          style={[
            styles.messageBubble,
            isSent ? styles.sentBubble : styles.receivedBubble,
          ]}
        >
          <Text
            style={[
              styles.messageText,
              isSent ? styles.sentMessageText : styles.receivedMessageText,
            ]}
          >
            {item.message}
          </Text>
          <Text
            style={[
              styles.messageTime,
              isSent ? styles.sentMessageTime : styles.receivedMessageTime,
            ]}
          >
            {getRelativeTime(item.timestamp)}
          </Text>
        </View>
      </View>
    );
  };

  const renderContactItem = ({ item }: { item: typeof contacts[0] }) => (
    <TouchableOpacity
      style={[
        styles.contactItem,
        selectedContact?.id === item.id && styles.selectedContact,
      ]}
      onPress={() => setSelectedContact(item)}
    >
      <View style={styles.contactAvatar}>
        <Text style={styles.contactAvatarText}>{item.avatar}</Text>
      </View>
      <View style={styles.contactInfo}>
        <View style={styles.contactHeader}>
          <Text style={styles.contactName}>{item.name}</Text>
          <Text style={styles.contactTime}>{item.time}</Text>
        </View>
        <Text style={styles.contactRole}>{item.role}</Text>
        <Text style={styles.contactLastMessage} numberOfLines={1}>
          {item.lastMessage}
        </Text>
      </View>
      {item.unread > 0 && (
        <View style={styles.unreadBadge}>
          <Text style={styles.unreadText}>{item.unread}</Text>
        </View>
      )}
    </TouchableOpacity>
  );

  return (
    <View style={styles.container}>
      {/* Contact List */}
      <View style={styles.contactList}>
        <Text style={styles.sectionTitle}>Messages</Text>
        <FlatList
          data={contacts}
          renderItem={renderContactItem}
          keyExtractor={(item) => item.id}
          contentContainerStyle={styles.contactListContent}
          showsVerticalScrollIndicator={false}
        />
      </View>

      {/* Chat Area */}
      <View style={styles.chatArea}>
        {/* Chat Header */}
        <Surface style={styles.chatHeader} elevation={1}>
          <View style={styles.chatHeaderLeft}>
            <View style={styles.chatHeaderAvatar}>
              <Text style={styles.chatHeaderAvatarText}>
                {selectedContact?.avatar}
              </Text>
            </View>
            <View>
              <Text style={styles.chatHeaderName}>{selectedContact?.name}</Text>
              <Text style={styles.chatHeaderRole}>{selectedContact?.role}</Text>
            </View>
          </View>
          <View style={styles.chatHeaderActions}>
            <IconButton icon="phone" size={20} color={COLORS.primary} />
            <IconButton icon="video" size={20} color={COLORS.primary} />
          </View>
        </Surface>

        {/* Messages */}
        <FlatList
          ref={flatListRef}
          data={messages.filter(
            (m) =>
              m.senderId === user?.id ||
              m.receiverId === selectedContact?.id ||
              m.senderId === selectedContact?.id
          )}
          renderItem={renderMessageItem}
          keyExtractor={(item) => item.id}
          contentContainerStyle={styles.messagesContent}
          onContentSizeChange={() => flatListRef.current?.scrollToEnd({ animated: true })}
          onLayout={() => flatListRef.current?.scrollToEnd({ animated: true })}
          showsVerticalScrollIndicator={false}
        />

        {/* Message Input */}
        <KeyboardAvoidingView
          behavior={Platform.OS === 'ios' ? 'padding' : undefined}
          keyboardVerticalOffset={Platform.OS === 'ios' ? 90 : 0}
        >
          <Surface style={styles.inputContainer} elevation={2}>
            <TextInput
              style={styles.messageInput}
              value={messageInput}
              onChangeText={setMessageInput}
              placeholder="Type a message..."
              multiline
              maxLength={500}
            />
            <TouchableOpacity
              style={[
                styles.sendButton,
                !messageInput.trim() && styles.sendButtonDisabled,
              ]}
              onPress={handleSend}
              disabled={!messageInput.trim() || isSending}
            >
              {isSending ? (
                <ActivityIndicator size="small" color="#FFFFFF" />
              ) : (
                <Text style={styles.sendButtonText}>Send</Text>
              )}
            </TouchableOpacity>
          </Surface>
        </KeyboardAvoidingView>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F9FAFB',
  },
  contactList: {
    width: 100,
    backgroundColor: '#FFFFFF',
    borderRightWidth: 1,
    borderRightColor: '#E5E7EB',
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#1F2937',
    padding: 16,
  },
  contactListContent: {
    paddingBottom: 16,
  },
  contactItem: {
    padding: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#F3F4F6',
  },
  selectedContact: {
    backgroundColor: COLORS.primary + '10',
  },
  contactAvatar: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: COLORS.primary + '20',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 8,
  },
  contactAvatarText: {
    fontSize: 14,
    fontWeight: 'bold',
    color: COLORS.primary,
  },
  contactInfo: {},
  contactHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  contactName: {
    fontSize: 12,
    fontWeight: '600',
    color: '#1F2937',
  },
  contactTime: {
    fontSize: 10,
    color: '#9CA3AF',
  },
  contactRole: {
    fontSize: 10,
    color: '#6B7280',
  },
  contactLastMessage: {
    fontSize: 11,
    color: '#9CA3AF',
    marginTop: 2,
  },
  unreadBadge: {
    backgroundColor: COLORS.primary,
    borderRadius: 10,
    minWidth: 20,
    height: 20,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 6,
    marginTop: 8,
  },
  unreadText: {
    color: '#FFFFFF',
    fontSize: 10,
    fontWeight: 'bold',
  },
  chatArea: {
    flex: 1,
    backgroundColor: '#F9FAFB',
  },
  chatHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: 12,
    backgroundColor: '#FFFFFF',
  },
  chatHeaderLeft: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  chatHeaderAvatar: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: COLORS.primary + '20',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  chatHeaderAvatarText: {
    fontSize: 14,
    fontWeight: 'bold',
    color: COLORS.primary,
  },
  chatHeaderName: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#1F2937',
  },
  chatHeaderRole: {
    fontSize: 12,
    color: '#6B7280',
  },
  chatHeaderActions: {
    flexDirection: 'row',
  },
  messagesContent: {
    padding: 16,
  },
  messageContainer: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    marginBottom: 12,
  },
  sentMessage: {
    justifyContent: 'flex-end',
  },
  receivedMessage: {
    justifyContent: 'flex-start',
  },
  messageAvatar: {
    marginRight: 8,
  },
  messageBubble: {
    maxWidth: '75%',
    padding: 12,
    borderRadius: 16,
  },
  sentBubble: {
    backgroundColor: COLORS.primary,
    borderBottomRightRadius: 4,
  },
  receivedBubble: {
    backgroundColor: '#FFFFFF',
    borderBottomLeftRadius: 4,
  },
  messageText: {
    fontSize: 14,
  },
  sentMessageText: {
    color: '#FFFFFF',
  },
  receivedMessageText: {
    color: '#1F2937',
  },
  messageTime: {
    fontSize: 10,
    marginTop: 4,
  },
  sentMessageTime: {
    color: 'rgba(255, 255, 255, 0.7)',
    textAlign: 'right',
  },
  receivedMessageTime: {
    color: '#9CA3AF',
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 8,
    backgroundColor: '#FFFFFF',
  },
  messageInput: {
    flex: 1,
    backgroundColor: '#F3F4F6',
    borderRadius: 20,
    paddingHorizontal: 16,
    paddingVertical: 8,
    maxHeight: 100,
    marginRight: 8,
  },
  sendButton: {
    backgroundColor: COLORS.primary,
    borderRadius: 20,
    paddingHorizontal: 16,
    paddingVertical: 10,
    justifyContent: 'center',
    alignItems: 'center',
  },
  sendButtonDisabled: {
    backgroundColor: '#D1D5DB',
  },
  sendButtonText: {
    color: '#FFFFFF',
    fontWeight: '600',
    fontSize: 14,
  },
});
