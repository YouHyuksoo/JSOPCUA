'use client';

import { useEffect, useState } from 'react';
import { getLines, deleteLine } from '@/lib/api/lines';
import { Line } from '@/lib/types/line';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import DeleteDialog from '@/components/DeleteDialog';
import { toast } from 'sonner';
import { Plus, Search, Edit, Trash2, Loader2, Database } from 'lucide-react';

export default function LinesPage() {
  const [lines, setLines] = useState<Line[]>([]);
  const [loading, setLoading] = useState(true);
  const [deleteId, setDeleteId] = useState<number | null>(null);
  const [searchTerm, setSearchTerm] = useState('');

  const fetchLines = async () => {
    try {
      const data = await getLines();
      setLines(data.items);
    } catch (error) {
      toast.error('Failed to load lines');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLines();
  }, []);

  const handleDelete = async () => {
    if (!deleteId) return;
    try {
      await deleteLine(deleteId);
      toast.success('Line deleted successfully');
      setDeleteId(null);
      fetchLines();
    } catch (error) {
      toast.error('Failed to delete line');
    }
  };

  const filteredLines = lines.filter(
    (line) =>
      (line.name?.toLowerCase() || '').includes(searchTerm.toLowerCase()) ||
      (line.code?.toLowerCase() || '').includes(searchTerm.toLowerCase())
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <Loader2 className="h-8 w-8 animate-spin text-blue-500" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white flex items-center gap-2">
            <Database className="h-8 w-8" />
            Production Lines
          </h1>
          <p className="text-gray-400 mt-1">Manage production lines and facilities</p>
        </div>
        <Link href="/lines/new">
          <Button className="bg-blue-600 hover:bg-blue-700">
            <Plus className="h-4 w-4 mr-2" />
            New Line
          </Button>
        </Link>
      </div>

      <Card className="bg-gray-900 border-gray-800">
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="text-white">Lines ({filteredLines.length})</CardTitle>
            <div className="relative w-64">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <Input
                placeholder="Search lines..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 bg-gray-800 border-gray-700 text-white"
              />
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="rounded-lg border border-gray-800 overflow-hidden">
            <Table>
              <TableHeader className="bg-gray-800">
                <TableRow className="hover:bg-gray-800">
                  <TableHead className="text-gray-400">ID</TableHead>
                  <TableHead className="text-gray-400">Name</TableHead>
                  <TableHead className="text-gray-400">Code</TableHead>
                  <TableHead className="text-gray-400">Created</TableHead>
                  <TableHead className="text-gray-400 text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredLines.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={5} className="text-center text-gray-500 py-8">
                      No lines found
                    </TableCell>
                  </TableRow>
                ) : (
                  filteredLines.map((line) => (
                    <TableRow
                      key={line.id}
                      className="border-gray-800 hover:bg-gray-800/50"
                    >
                      <TableCell className="font-medium text-white">{line.id}</TableCell>
                      <TableCell className="text-white font-semibold">{line.name}</TableCell>
                      <TableCell className="text-gray-300">
                        <span className="px-2 py-1 bg-blue-500/10 text-blue-400 rounded text-xs font-mono">
                          {line.code}
                        </span>
                      </TableCell>
                      <TableCell className="text-gray-400">
                        {new Date(line.created_at).toLocaleDateString()}
                      </TableCell>
                      <TableCell className="text-right space-x-2">
                        <Link href={`/lines/${line.id}`}>
                          <Button size="sm" variant="outline" className="bg-gray-800 border-gray-700 hover:bg-gray-700">
                            <Edit className="h-4 w-4" />
                          </Button>
                        </Link>
                        <Button
                          size="sm"
                          variant="destructive"
                          onClick={() => setDeleteId(line.id)}
                          className="bg-red-500/10 text-red-500 hover:bg-red-500/20"
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>

      <DeleteDialog
        open={deleteId !== null}
        onOpenChange={(open) => !open && setDeleteId(null)}
        onConfirm={handleDelete}
      />
    </div>
  );
}
