import React, { useState, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TextInput,
  TouchableOpacity,
  Alert,
} from 'react-native';
import { useFocusEffect, useRouter } from 'expo-router';
import { ShoppingListItem } from '../../src/types/coupon';
import {
  getAllShoppingListItems,
  addShoppingListItem,
  toggleShoppingListItem,
  removeShoppingListItem,
  clearCheckedItems,
} from '../../src/db/shoppingListRepository';
import { EmptyState } from '../../src/components/EmptyState';

export default function ShoppingListScreen() {
  const [items, setItems] = useState<ShoppingListItem[]>([]);
  const [newItem, setNewItem] = useState('');
  const router = useRouter();

  const loadItems = useCallback(async () => {
    try {
      const data = await getAllShoppingListItems();
      setItems(data);
    } catch (error) {
      console.error('Failed to load shopping list:', error);
    }
  }, []);

  useFocusEffect(
    useCallback(() => {
      loadItems();
    }, [loadItems])
  );

  const handleAddItem = async () => {
    const description = newItem.trim();
    if (!description) return;

    await addShoppingListItem(description);
    setNewItem('');
    loadItems();
  };

  const handleToggle = async (id: string) => {
    await toggleShoppingListItem(id);
    loadItems();
  };

  const handleRemove = (id: string, description: string) => {
    Alert.alert('Remove item', `Remove "${description}" from your list?`, [
      { text: 'Cancel', style: 'cancel' },
      {
        text: 'Remove',
        style: 'destructive',
        onPress: async () => {
          await removeShoppingListItem(id);
          loadItems();
        },
      },
    ]);
  };

  const handleClearChecked = () => {
    const checkedCount = items.filter((i) => i.isChecked).length;
    if (checkedCount === 0) return;

    Alert.alert('Clear checked items', `Remove ${checkedCount} checked item(s)?`, [
      { text: 'Cancel', style: 'cancel' },
      {
        text: 'Clear',
        onPress: async () => {
          await clearCheckedItems();
          loadItems();
        },
      },
    ]);
  };

  const renderItem = ({ item }: { item: ShoppingListItem }) => (
    <View style={styles.itemRow}>
      <TouchableOpacity
        style={[styles.checkbox, item.isChecked && styles.checkboxChecked]}
        onPress={() => handleToggle(item.id)}
      >
        {item.isChecked && <Text style={styles.checkmark}>✓</Text>}
      </TouchableOpacity>

      <View style={styles.itemContent}>
        <Text style={[styles.itemText, item.isChecked && styles.itemTextChecked]}>
          {item.description}
        </Text>
        {item.matchedCouponIds.length > 0 && !item.isChecked && (
          <TouchableOpacity
            onPress={() => router.push('/(tabs)/')}
          >
            <Text style={styles.couponMatch}>
              {item.matchedCouponIds.length} coupon{item.matchedCouponIds.length !== 1 ? 's' : ''} available
            </Text>
          </TouchableOpacity>
        )}
      </View>

      <TouchableOpacity
        style={styles.removeButton}
        onPress={() => handleRemove(item.id, item.description)}
        hitSlop={{ top: 10, bottom: 10, left: 10, right: 10 }}
      >
        <Text style={styles.removeText}>×</Text>
      </TouchableOpacity>
    </View>
  );

  const checkedCount = items.filter((i) => i.isChecked).length;

  return (
    <View style={styles.container}>
      <View style={styles.headerSection}>
        <View style={styles.headerRow}>
          <Text style={styles.title}>Shopping List</Text>
          {checkedCount > 0 && (
            <TouchableOpacity onPress={handleClearChecked}>
              <Text style={styles.clearText}>Clear checked</Text>
            </TouchableOpacity>
          )}
        </View>
      </View>

      <View style={styles.inputContainer}>
        <TextInput
          style={styles.input}
          placeholder="Add an item..."
          placeholderTextColor="#9CA3AF"
          value={newItem}
          onChangeText={setNewItem}
          onSubmitEditing={handleAddItem}
          returnKeyType="done"
        />
        <TouchableOpacity style={styles.addButton} onPress={handleAddItem}>
          <Text style={styles.addButtonText}>+</Text>
        </TouchableOpacity>
      </View>

      <FlatList
        data={items}
        keyExtractor={(item) => item.id}
        renderItem={renderItem}
        contentContainerStyle={items.length === 0 ? styles.emptyList : styles.list}
        ListEmptyComponent={
          <EmptyState
            title="List is empty"
            message="Add items to your shopping list and we'll match them with your coupons."
          />
        }
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F9FAFB',
  },
  headerSection: {
    paddingHorizontal: 20,
    paddingTop: 60,
    paddingBottom: 12,
    backgroundColor: '#FFFFFF',
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
  },
  headerRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-end',
  },
  title: {
    fontSize: 28,
    fontWeight: '800',
    color: '#1F2937',
  },
  clearText: {
    fontSize: 14,
    color: '#EF4444',
    fontWeight: '500',
  },
  inputContainer: {
    flexDirection: 'row',
    paddingHorizontal: 16,
    paddingVertical: 12,
    backgroundColor: '#FFFFFF',
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
    gap: 10,
  },
  input: {
    flex: 1,
    backgroundColor: '#F3F4F6',
    borderRadius: 10,
    paddingHorizontal: 14,
    paddingVertical: 10,
    fontSize: 15,
    color: '#1F2937',
  },
  addButton: {
    backgroundColor: '#4F46E5',
    width: 42,
    height: 42,
    borderRadius: 10,
    justifyContent: 'center',
    alignItems: 'center',
  },
  addButtonText: {
    color: '#FFFFFF',
    fontSize: 22,
    fontWeight: '600',
    lineHeight: 24,
  },
  list: {
    paddingVertical: 8,
  },
  emptyList: {
    flex: 1,
  },
  itemRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingVertical: 14,
    backgroundColor: '#FFFFFF',
    borderBottomWidth: 1,
    borderBottomColor: '#F3F4F6',
  },
  checkbox: {
    width: 24,
    height: 24,
    borderRadius: 6,
    borderWidth: 2,
    borderColor: '#D1D5DB',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  checkboxChecked: {
    backgroundColor: '#4F46E5',
    borderColor: '#4F46E5',
  },
  checkmark: {
    color: '#FFFFFF',
    fontSize: 14,
    fontWeight: '700',
  },
  itemContent: {
    flex: 1,
  },
  itemText: {
    fontSize: 16,
    color: '#1F2937',
  },
  itemTextChecked: {
    color: '#9CA3AF',
    textDecorationLine: 'line-through',
  },
  couponMatch: {
    fontSize: 13,
    color: '#4F46E5',
    fontWeight: '500',
    marginTop: 2,
  },
  removeButton: {
    marginLeft: 12,
    padding: 4,
  },
  removeText: {
    fontSize: 20,
    color: '#9CA3AF',
    fontWeight: '500',
  },
});
