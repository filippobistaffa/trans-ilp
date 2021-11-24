import torch
import torch.nn as nn
import torch.nn.functional as F
import math

class Embedder(nn.Module):
    def __init__(self, input_size, d_model, num_categories=[]):
        super().__init__()
        self.n = num_categories

        self.continuous_size = input_size - len(num_categories)
        self.categorical_size = len(num_categories)

        self.categorical_embeddings = nn.ModuleList([
            nn.Embedding(n + 1, d_model, padding_idx=n) for n in num_categories])

        self.embedding = nn.Linear(d_model + self.continuous_size, d_model)

    def forward(self, x):
        categorical = x[:, :, :self.categorical_size]
        continuous = x[:, :, self.categorical_size:]

        categorical_embedded = torch.stack([
            emb(categorical[:, :, i] % (self.n[i] + 1))
            for i, emb in enumerate(self.categorical_embeddings)], dim=-1).sum(dim=-1)

        return self.embedding(torch.cat(
            [categorical_embedded, continuous],
            dim=2))

class MultiHeadAttention(nn.Module):
    def __init__(self, d_model, nhead, d_q=None, d_k=None, d_v=None):
        super().__init__()
        self.d_model = d_model
        self.nhead = nhead
        self.d_head = d_model // nhead

        self.w_q = nn.Linear(d_q if d_q else d_model, d_model, bias=False)
        self.w_k = nn.Linear(d_k if d_k else d_model, d_model, bias=False)
        self.w_v = nn.Linear(d_v if d_v else d_model, d_model, bias=False)
        self.w_o = nn.Linear(d_model, d_model, bias=False)

    def forward(self, q, k, v, mask=None):
        batch_size = q.size(0)

        q = self.w_q(q).view(batch_size, self.nhead, -1, self.d_head)
        k = self.w_k(k).view(batch_size, self.nhead, -1, self.d_head)
        v = self.w_v(v).view(batch_size, self.nhead, -1, self.d_head)

        u = torch.matmul(q, k.transpose(-2, -1)) / math.sqrt(self.d_head)
        if mask is not None:
            u = u.masked_fill(mask.view(batch_size, 1, 1, -1), float("-inf"))

        attn = F.softmax(u, dim=-1)
        attn_applied = torch.matmul(attn, v)

        return self.w_o(attn_applied.view(batch_size, -1, self.d_model))

class Encoder(nn.Module):
    def __init__(self, d_model, nhead, dim_feedforward, num_layers):
        super().__init__()
        self.attn = nn.ModuleList([
            MultiHeadAttention(d_model, nhead) for _ in range(num_layers)])

        self.ffrd = nn.ModuleList([
            nn.Sequential(
                nn.Linear(d_model, dim_feedforward),
                nn.ReLU(),
                nn.Linear(dim_feedforward, d_model))
            for _ in range(num_layers)])

        self.norm1 = nn.ModuleList([
            nn.LayerNorm(d_model) for _ in range(num_layers)])

        self.norm2 = nn.ModuleList([
            nn.LayerNorm(d_model) for _ in range(num_layers)])

    def forward(self, x, mask=None):
        for attn, ffrd, norm1, norm2 in zip(self.attn, self.ffrd, self.norm1, self.norm2):
            x = norm1(x + attn(x, x, x, mask))
            x = norm2(x + ffrd(x))
        return x

class Decoder(nn.Module):
    def __init__(self, d_model, nhead):
        super().__init__()
        self.attn = MultiHeadAttention(d_model, nhead, d_q = 2 * d_model)
        self.w_k = nn.Linear(d_model, d_model, bias=False)

    def forward(self, x, h, mask, C=10):
        batch_size, seq_len, d_model = x.size()

        q = self.attn(h, x, x, mask)
        k = self.w_k(x)

        u = torch.matmul(q, k.transpose(-2, -1)) / math.sqrt(d_model)

        if C == -1:
            return u

        u = C * torch.tanh(u)
        u = u.masked_fill(mask.view(batch_size, 1, seq_len), float('-inf'))

        return F.softmax(u.view(batch_size, seq_len), dim=-1)

class Actor(nn.Module):
    def __init__(self, input_size, d_model, nhead, dim_feedforward, num_layers, num_categories=[]):
        super().__init__()
        self.embedder = Embedder(input_size, d_model, num_categories)
        self.encoder = Encoder(d_model, nhead, dim_feedforward, num_layers)
        self.decoder_pi = Decoder(d_model, nhead)
        self.decoder_v = Decoder(d_model, nhead)

        self.v = nn.Parameter(torch.empty(1, 1, d_model).uniform_(
            -1 / math.sqrt(d_model), 1 / math.sqrt(d_model)))

    def _add_token(self, context):
        batch_size = context.size(0)
        return torch.cat([
            self.v.repeat(batch_size, 1, 1),
            context
        ], dim=1)

    def _get_hidden_state(self, context, coalition):
        return torch.cat([
            context.mean(dim=1, keepdim=True),
            context.gather(1, 1 + coalition.unsqueeze(-1).expand([-1, -1, context.size(2)])
                ).mean(dim=1, keepdim=True)], dim=2)

    def _get_mask(self, context, coalition):
        batch_size, seq_len, _ = context.size()
        mask = torch.zeros(batch_size, seq_len, dtype=torch.bool, device=self.v.device)
        mask.scatter_(1, 1 + coalition, True)
        mask[:, 0] = False
        return mask

    def forward(self, participants, collective):
        embedded = self.embedder(participants)

        padding_mask = torch.all((participants == -1), dim=-1)

        context = self.encoder(embedded, mask=padding_mask)
        context = self._add_token(context)

        hidden = self._get_hidden_state(context, collective)
        mask = self._get_mask(context, collective)
        mask[:, 1:] = torch.logical_or(mask[:, 1:], padding_mask)

        probs = self.decoder_pi(context, hidden, mask)
        v = self.decoder_v(context, hidden, mask, C=-1)

        value = torch.matmul(v, probs.unsqueeze(-1)).squeeze()

        return probs, value
