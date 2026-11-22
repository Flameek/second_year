#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Бинарное дерево поиска для лабораторной работы 5."""

from __future__ import annotations

from collections import deque


class Node:
    """Узел BST с ключом и ссылками на два поддерева."""

    __slots__ = ("key", "left", "right")

    def __init__(self, key: int) -> None:
        self.key = key
        self.left: Node | None = None
        self.right: Node | None = None


class BST:
    """Бинарное дерево поиска без дубликатов.

    Ключи слева от каждого узла меньше его ключа, а справа — больше.
    Вставка, поиск и удаление занимают O(h + 1) времени в непустом дереве.
    """

    def __init__(self) -> None:
        self.root: Node | None = None

    def insert(self, key: int) -> None:
        """Вставляет ключ, если его ещё нет в дереве."""
        if self.root is None:
            self.root = Node(key)
            return

        node = self.root
        while node.key != key:
            if key < node.key:
                if node.left is None:
                    node.left = Node(key)
                    return
                node = node.left
            else:
                if node.right is None:
                    node.right = Node(key)
                    return
                node = node.right

    def search(self, key: int) -> bool:
        """Возвращает True, если дерево содержит ключ."""
        node = self.root
        while node is not None:
            if key == node.key:
                return True
            node = node.left if key < node.key else node.right
        return False

    def delete(self, key: int) -> None:
        """Удаляет ключ, заменяя узел с двумя детьми его преемником."""
        parent = None
        node = self.root
        while node is not None and node.key != key:
            parent = node
            node = node.left if key < node.key else node.right
        if node is None:
            return

        if node.left is not None and node.right is not None:
            successor_parent = node
            successor = node.right
            while successor.left is not None:
                successor_parent = successor
                successor = successor.left
            node.key = successor.key
            parent, node = successor_parent, successor

        # Здесь у физически удаляемого узла не более одного ребёнка.
        child = node.left if node.left is not None else node.right
        if parent is None:
            self.root = child
        elif parent.left is node:
            parent.left = child
        else:
            parent.right = child

    def in_order(self) -> list[int]:
        """Рекурсивно обходит дерево в порядке лево, узел, право."""
        keys: list[int] = []

        def visit(node: Node | None) -> None:
            if node is not None:
                visit(node.left)
                keys.append(node.key)
                visit(node.right)

        visit(self.root)
        return keys

    def pre_order(self) -> list[int]:
        """Рекурсивно обходит дерево в порядке узел, лево, право."""
        keys: list[int] = []

        def visit(node: Node | None) -> None:
            if node is not None:
                keys.append(node.key)
                visit(node.left)
                visit(node.right)

        visit(self.root)
        return keys

    def post_order(self) -> list[int]:
        """Рекурсивно обходит дерево в порядке лево, право, узел."""
        keys: list[int] = []

        def visit(node: Node | None) -> None:
            if node is not None:
                visit(node.left)
                visit(node.right)
                keys.append(node.key)

        visit(self.root)
        return keys

    def level_order(self) -> list[int]:
        """Обходит дерево по уровням слева направо через очередь."""
        if self.root is None:
            return []

        keys: list[int] = []
        queue = deque([self.root])
        while queue:
            node = queue.popleft()
            keys.append(node.key)
            if node.left is not None:
                queue.append(node.left)
            if node.right is not None:
                queue.append(node.right)
        return keys

    def height(self) -> int:
        """Возвращает высоту в рёбрах или -1 для пустого дерева."""
        if self.root is None:
            return -1

        height = 0
        stack = [(self.root, 0)]
        while stack:
            node, depth = stack.pop()
            height = max(height, depth)
            if node.left is not None:
                stack.append((node.left, depth + 1))
            if node.right is not None:
                stack.append((node.right, depth + 1))
        return height

    def size(self) -> int:
        """Возвращает число узлов в дереве."""
        if self.root is None:
            return 0

        count = 0
        stack = [self.root]
        while stack:
            node = stack.pop()
            count += 1
            if node.left is not None:
                stack.append(node.left)
            if node.right is not None:
                stack.append(node.right)
        return count
